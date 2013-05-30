# -*- coding: utf-8 -*-

"""WebHelpers used in SkyLines."""

from __future__ import absolute_import

import datetime
import simplejson as json
from urllib import urlencode

from flask import flash
from webhelpers import date, feedgenerator, html, number, misc, text

from .string import *
from .country import *
from skylines.lib.formatter.numbers import *
from skylines.lib.formatter.datetime import *
from skylines.lib.formatter.units import *
from skylines.lib.markdown import markdown

# Jinja2 doesn't seem to have min/max... strange!
min = min
max = max


def url(base_url='/', **params):
    if not isinstance(base_url, basestring) and hasattr(base_url, '__iter__'):
        base_url = '/'.join(base_url)

    if params:
        return '?'.join((base_url, urlencode(params)))

    return base_url
