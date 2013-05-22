# -*- coding: utf-8 -*-

"""WebHelpers used in SkyLines."""

from __future__ import absolute_import

import datetime
import simplejson as json

from tg import flash, url
from webhelpers import date, feedgenerator, html, number, misc, text

from .string import *
from .country import *
from skylines.lib.formatter.numbers import *
from skylines.lib.formatter.datetime import *
from skylines.lib.formatter.units import *
from skylines.lib.markdown import markdown

# The dict implementation of Jinja2 only works for keyword parameters,
# but not for merging to dictionaries. We export the builtin Python dict()
# function here to get around that problem for building URLs.
dict = dict

# Jinja2 doesn't seem to have min/max... strange!
min = min
max = max
