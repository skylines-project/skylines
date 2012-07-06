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


def format_flight_title(flight):
    title = format_number(flight.olc_classic_distance / 1000) + ' km'
    title = title + ' on ' + format_date(flight.takeoff_time)

    tagline = ''
    if flight.pilot:
        tagline = tagline + ' by ' + unicode(flight.pilot)

    if flight.co_pilot:
        tagline = tagline + ' and ' + unicode(flight.co_pilot)

    return title, tagline
