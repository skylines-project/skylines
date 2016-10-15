# -*- coding: utf-8 -*-

"""WebHelpers used in SkyLines."""

# flake8: noqa

from __future__ import absolute_import

import datetime
from urllib import urlencode

from flask import flash
from webhelpers import date, feedgenerator, html, number, misc, text

from .country import *
from skylines.lib.formatter.units import get_setting_name
from skylines.lib.datetime import to_seconds_of_day
from skylines.frontend.views.upload import UploadStatus

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
