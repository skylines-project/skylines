# -*- coding: utf-8 -*-

"""WebHelpers used in SkyLines."""

# flake8: noqa

from __future__ import absolute_import

import datetime
from urllib import urlencode

from flask import flash, json
from webhelpers import date, feedgenerator, html, number, misc, text

from .string import *
from .country import *
from skylines.lib.formatter.numbers import *
from skylines.lib.formatter.datetime import *
from skylines.lib.formatter.units import *
from skylines.lib.markdown_ import markdown
from skylines.lib.datetime import to_seconds_of_day
from skylines.frontend.views.upload import UploadStatus

from pygments import highlight
from pygments.lexers import HtmlLexer
from pygments.formatters import HtmlFormatter

html_formatter = HtmlFormatter(style='tango', nowrap=True)

# Jinja2 doesn't seem to have min/max... strange!
min = min
max = max


def url(base_url='/', **params):
    if not isinstance(base_url, basestring) and hasattr(base_url, '__iter__'):
        base_url = '/'.join(base_url)

    if params:
        return '?'.join((base_url, urlencode(params)))

    return base_url


def pygmentize(html):
    return highlight(html, HtmlLexer(), html_formatter)


def pygments_styles():
    return html_formatter.get_style_defs('.highlight')
