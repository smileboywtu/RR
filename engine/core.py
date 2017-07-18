# -*- coding: utf-8 -*-

from __future__ import absolute_import

from babel.support import Translations
from jinja2 import Environment, FileSystemLoader

from . import templateext
from .settings import TEMPLATE_DIR, LOCALE_DIR
from .settings import user_setting

# Jinja2 Extensions
JINJA2_EXTENSIONS = [
    "jinja2.ext.i18n",
    "jinja2.ext.with_",
]

core_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    extensions=JINJA2_EXTENSIONS,
    autoescape=True
)

# setup locale
core_env.install_gettext_translations(
    Translations.load(LOCALE_DIR, user_setting.get("default_locale")))

# add ext
attrs = dir(templateext)
for attr in attrs:
    func = getattr(templateext, attr)
    if hasattr(func, '__call__') and hasattr(func, 'func_name'):
        core_env.filters[attr] = func
