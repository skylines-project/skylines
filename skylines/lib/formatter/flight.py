from tg.i18n import ugettext as _
from skylines.lib.formatter import format_date
from skylines.lib.formatter.units import format_distance

__all__ = ['format_flight_title']


def format_flight_title(flight):
    title = _('{distance} on {date}').format(distance=format_distance(flight.olc_classic_distance),
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
