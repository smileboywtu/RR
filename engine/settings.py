# -*- coding: utf-8 -*-


import logging.config

import hjson
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

user_setting = {}
with open(os.path.join(BASE_DIR, "config.hjson")) as fp:
    user_setting = hjson.loads(fp.read())

# setup static directory for render
TEMPLATE_DIR = os.path.join(BASE_DIR, "static", "html")
LOCALE_DIR = os.path.join(BASE_DIR, "translation")
ASSETS_DIR = os.path.join(BASE_DIR, "static", "assets")
STYLE_DIR = os.path.join(BASE_DIR, "static", "css")
WKH2P_PATH = os.path.join(BASE_DIR, "3rd", "tools", "wkhtmltoimage")

# module logging config
# config with dict logging configure
LOGGING_CONF_DICT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        },
        "verbose": {
            "format": "%(asctime)s %(levelname)s %(pathname)s %(module)s %(filename)s %(funcName)s %(lineno)d %(message)s"
        },
    },
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
            "level": "DEBUG"
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple"
        },
        "file": {
            "class": "logging.handlers.WatchedFileHandler",
            "level": "DEBUG",
            "formatter": "verbose",
            "filename": "/var/log/web/infinite.log",
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "engine": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": False
        },
        "common": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False
        },
        "source": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False
        },
        "render": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG"
    },
}

logging.config.dictConfig(LOGGING_CONF_DICT)
