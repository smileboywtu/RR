# -*- coding: utf-8 -*-

"""

    report worker absolute class


"""

from __future__ import absolute_import

import logging
from io import BytesIO

import os
from abc import ABCMeta, abstractmethod
from weasyprint import default_url_fetcher, CSS, HTML

from common.exceptions import DirectoryDoesNotExist
from .core import core_env
from .settings import ASSETS_DIR, STYLE_DIR

logger = logging.getLogger("engine")


class FileStorage(object):
    """write pdf to local storage"""

    def store(self, bytes, path):
        """
        write bytes into path

        :param bytes:
        :param path:
        :return:
        """
        parent_dir = os.path.dirname(path)
        if not os.path.exists(parent_dir):
            raise DirectoryDoesNotExist("%s is not exist", parent_dir)
        with open(path, "wb") as writer:
            return writer.write(bytes)
        return 0


class SourceMixin(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_source_data(self):
        """
        get the source data for render template

        :return:
        """
        raise NotImplementedError("function: get_source_data should be implemented")


class RenderMixin(object):
    def render(self, tlp, data):
        """
        render data into template
        :param tlp: html template
        :param data:
        :return:
        """
        html_tlp = core_env.get_template(tlp)
        return html_tlp.render(data)


class Converter(object):
    """convert html to pdf stream"""

    def _image_fetcher(self, url):
        """fetch the image files from dir
        all the image url must start with `image:` to
        enable image file fetcher

        example code:

            html = "<img src="image:1.png">

        :param url: image url
        :return: dict
        """
        if url.startswith("image:"):
            filename = url.split("image:")[-1]
            # set image dir
            filepath = os.path.join(self.image_dir, filename)
            if not os.path.exists(filepath):
                filepath = os.path.join(ASSETS_DIR, filename)

            return dict(file_obj=file(filepath), mime_type="image/png")
        else:
            return default_url_fetcher(url)

    def convert(self, html, css, dir=ASSETS_DIR):
        """convert html to pdf stream

        :param html: html string
        :return: document object
        """
        logger.debug("start html 2 pdf converter...")
        self.image_dir = dir
        css_objs = [CSS(filename=os.path.join(STYLE_DIR, file)) \
                    for file in css]
        document = HTML(string=html, url_fetcher=self._image_fetcher) \
            .render(stylesheets=css_objs)

        return document

    @staticmethod
    def save_pdf(documents, filename):
        """

        :param documents: list, documents objects
        :param filename: str, pdf filename
        :return: True of success
        """
        all_pages = []
        for doc in documents:
            all_pages.extend(doc.pages)

        assert all_pages != []
        # create a new documents with pages
        # then write to pdf
        documents[0].copy(all_pages).write_pdf(filename)
        return True

    def __call__(self, *args, **kwargs):
        """call this by default"""
        return self.convert(*args, **kwargs)


class Worker(SourceMixin, RenderMixin, FileStorage):
    """report render worker"""

    __metaclass__ = ABCMeta

    def __init__(self, template, path, css=("customer.css",)):
        self.__converter = Converter()
        self.template = template
        self.css = css
        self.path = path

    @abstractmethod
    def build_images(self):
        """
        build the image need for render pdf
        example:
        <img src={{ "image:img/report_logo.png"}}> load image from assets/image dir

        you write any image with echarts and jq then convert it to png use
        wkhtml2png tool

        :return:
        """
        raise NotImplementedError("function: build image must be implemented")

    def run(self):
        """
        1. get source data
        2. render into html
        3. build images
        4. render into pdf use wp

        :return:
        """
        data = self.get_source_data()
        if not data:
            logger.warning("data is empty")

        html = self.render(self.template, data)
        if not html:
            logging.error("template is empty")
            return False

        try:
            # build image
            self.build_images()
            _pdf = BytesIO()
            document = self.__converter(html, self.css)
            self.__converter.save_pdf([document, ], _pdf)
            self.store(_pdf.getvalue(), self.path)
            return True
        except Exception as e:
            logger.error(str(e))
            return False
