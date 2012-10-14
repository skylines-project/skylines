# -*- coding: utf-8 -*-

"""WebHelpers used in SkyLines."""

from webhelpers import date, feedgenerator, html, number, misc, text
import simplejson as json
from tg import flash, request
from datetime import timedelta
from sets import Set
from inspect import currentframe, getframeinfo
from os.path import normpath

from babel.dates import format_date, format_time, format_datetime
from babel.numbers import format_number, format_decimal

from markdown import Markdown

from skylines.lib.units import format_distance
from skylines.lib.urlize import UrlizeExtension


urlize = UrlizeExtension()
markdown = Markdown(extensions=['nl2br', urlize], safe_mode='escape')


def isoformat_utc(dt):
    return dt.isoformat() + 'Z'


def format_timedelta(delta):
    if isinstance(delta, timedelta):
        seconds = delta.total_seconds()
    else:
        seconds = delta

    return '%d:%02d' % (seconds / 3600, seconds % 3600 / 60)


def format_flight_title(flight):
    title = format_distance(flight.olc_classic_distance)
    title = title + ' on ' + format_date(flight.date_local)

    tagline = ''
    if flight.pilot:
        tagline = tagline + ' by ' + unicode(flight.pilot)

    if flight.co_pilot:
        tagline = tagline + ' and ' + unicode(flight.co_pilot)

    return title, tagline


def truncate(string, length=50, suffix='...', smart=False):
    if len(string) <= length:
        return string
    elif smart:
        return string[:(length - len(suffix))].rsplit(' ', 1)[0] + suffix
    else:
        return string[:(length - len(suffix))] + suffix


def not_included_yet():
    # Create template_includes set if necessary
    if not hasattr(request, 'template_includes'):
        request.template_includes = Set()

    # Extract calling template filename
    filename = normpath(getframeinfo(currentframe(1)).filename)

    # Check whether template was already included before
    if filename in request.template_includes:
        return False

    # Remember that this template was included now
    request.template_includes.add(filename)
    return True


def string_if(str, condition):
    return str if condition else None
