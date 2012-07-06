# -*- coding: utf-8 -*-

"""WebHelpers used in SkyLines."""

from webhelpers import date, feedgenerator, html, number, misc, text
import simplejson as json
from tg.flash import flash
from datetime import timedelta

from babel.dates import format_date, format_time, format_datetime
from babel.numbers import format_number


def format_timedelta(delta):
    if isinstance(delta, timedelta):
        seconds = delta.total_seconds()
    else:
        seconds = delta

    return '%d:%02d' % (seconds / 3600, seconds % 3600 / 60)
