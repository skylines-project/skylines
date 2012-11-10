# -*- coding: utf-8 -*-

"""WebHelpers used in SkyLines."""

from webhelpers import date, feedgenerator, html, number, misc, text
import simplejson as json
from tg import flash
from tg.i18n import ugettext as _

from babel.dates import format_date, format_time, format_datetime
from babel.numbers import format_number, format_decimal

from skylines.lib.helpers.datetime import *
from skylines.lib.helpers.includeguard import not_included_yet
from skylines.lib.helpers.markdown import markdown
from skylines.lib.helpers.string import *
from skylines.lib.helpers.country import *
from skylines.lib.units import format_distance


def format_flight_title(flight):
    title = '{distance} on {date}'.format(distance=format_distance(flight.olc_classic_distance),
                                          date=format_date(flight.date_local))

    if flight.pilot is None:
        return title, ''

    if flight.co_pilot is None:
        tagline = (_('{something} by {pilot_name}').
                   format(something='',
                          pilot_name=unicode(flight.pilot)))
    else:
        tagline = (_('{something} by {pilot_name} and {co_pilot_name}').
                   format(something='',
                          pilot_name=unicode(flight.pilot),
                          co_pilot_name=unicode(flight.co_pilot)))

    return title, tagline
