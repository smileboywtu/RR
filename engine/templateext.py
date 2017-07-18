# -*- coding: utf-8 -*-


"""

    add your customer jinja2 template ext here
    as you need

    for mare information just read the `jinja2`
    documentations

"""
import datetime


def timestamp2fmt(timestamp, format):
    """
    Convert timestamp to format

    :param timestamp:
    :param formt:
    :return:
    """
    try:
        customer = datetime.datetime.fromtimestamp(timestamp).strftime(format)
    except:
        customer = ""
    return customer
