# -*- coding: utf-8 -*-


from __future__ import absolute_import

import logging
import shlex
import subprocess

import numpy as np
import os
from PIL import Image

from .exceptions import ProgramNotFoundError, DirectoryDoesNotExist

logger = logging.getLogger("common")


def html2image(exe_path, exe_args, html_content, out_path):
    """
    convert html to image with `wkhtmltoimage` tools

    :param exe_path: wkhtmltoimage path
    :param exe_args: wkhtmltoimage args or options
    :param html_content: utf-8 html source code
    :param out_path: output image path
    :return: bool
    """
    if not os.path.exists(exe_path):
        raise ProgramNotFoundError("%s not exists", exe_path)
    parent_dir = os.path.dirname(out_path)
    if not os.path.exists(parent_dir):
        raise DirectoryDoesNotExist("%s not exist", parent_dir)

    try:
        params = [exe_path]
        args = shlex.split(exe_args)
        params.extend(args)
        params += ["-", out_path]

        process = subprocess.Popen(params, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = process.communicate(html_content)
        if not err:
            return True
        logging.error(err)
        return False
    except Exception as e:
        logging.error(str(e))
        return False


def change_background_color(self, filepath, color=(255, 255, 255)):
    """
    Change background white color to color

    :param filepath:
    :param color:
    :return:
    """
    im = Image.open(filepath)
    im = im.convert("RGBA")

    data = np.array(im)  # "data" is a height x width x 4 numpy array
    red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability

    # Replace white with red... (leaves alpha values alone...)
    white_areas = (red == 255) & (blue == 255) & (green == 255)
    data[..., :-1][white_areas.T] = color  # Transpose back needed
    im2 = Image.fromarray(data)
    im2.save(filepath)


def suit_cropping(self, filein, fileout=None, watermark=True):
    """
    Crop Image
    :param filein:
    :param fileout:
    :param watermark:
    :return:
    """
    im_in = Image.open(filein)

    if im_in.mode == "RGB":
        im = im_in.convert("L")
    if im_in.mode == "RGBA":
        im = im_in.convert("L")
    elif im_in.mode == "P":
        im = im_in.convert("L")
    else:
        im = im_in
    data = list(im.getdata())

    w, h = im.size  # width, height
    # print "size: (%d, %d)" % (w, h)
    if watermark:
        h -= 10
        data = data[:h * w]

    # s: start,  e: end
    s1_min = w - 1
    e1_max = 0
    s2_min = h - 1
    e2_max = 0
    s1_tmp = w - 1
    e1_tmp = 0

    s2_and_e2_tmp = 0

    for i, d in enumerate(data):
        x = i % w
        y = i // w
        if x == 0:
            if s1_min > s1_tmp:
                s1_min = s1_tmp
            if e1_max < e1_tmp:
                e1_max = e1_tmp

            if s2_and_e2_tmp:
                if s2_min > y:
                    s2_min = y
                if e2_max < y:
                    e2_max = y
            s1_tmp = w - 1
            e1_tmp = 0
            s2_and_e2_tmp = 0

        if d != 255:
            e1_tmp = x
            if s1_tmp == w - 1:
                s1_tmp = x
            s2_and_e2_tmp = 1

    widening_w = int((e1_max - s1_min) * 0.05)
    widening_h = int((e2_max - s2_min) * 0.05)

    widening_limit = True
    if widening_limit:
        limit = 22
        widening_w = limit if widening_w > limit else widening_w
        widening_h = limit if widening_h > limit else widening_h

    s1_crop = s1_min - widening_w if s1_min - widening_w > 0 else 0
    e1_crop = e1_max + widening_w if e1_max + widening_w < w else w - 1
    s2_crop = s2_min - widening_h if s2_min - widening_h > 0 else 0
    e2_crop = e2_max + widening_h if e2_max + widening_h < h else h - 1
    region = im_in.crop((s1_crop, s2_crop, e1_crop, e2_crop))

    region.save(fileout or filein)
