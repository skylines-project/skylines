# -*- coding: utf-8 -*-

"""WebHelpers used in SkyLines."""

from webhelpers import date, feedgenerator, html, number, misc, text
import simplejson as json
from tg import flash

from babel.dates import format_date, format_time, format_datetime
from babel.numbers import format_number, format_decimal

from skylines.lib.helpers.datetime import *
from skylines.lib.helpers.includeguard import not_included_yet
from skylines.lib.helpers.markdown import markdown
from skylines.lib.helpers.string import *
from skylines.lib.units import format_distance


def format_flight_title(flight):
    title = format_distance(flight.olc_classic_distance)
    title = title + ' on ' + format_date(flight.date_local)

    tagline = ''
    if flight.pilot:
        tagline = tagline + ' by ' + unicode(flight.pilot)

    if flight.co_pilot:
        tagline = tagline + ' and ' + unicode(flight.co_pilot)

    return title, tagline
