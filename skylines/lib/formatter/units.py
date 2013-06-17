from collections import namedtuple

from flask import g
from flask.ext.babel import lazy_gettext as l_

from .numbers import format_decimal

Unit = namedtuple('Unit', ['name', 'factor', 'format', 'decimal_places'])

distance_units = (
    Unit(u'm', 1, u'{0:.{1}f} m', 0),
    Unit(u'km', 1 / 1000., u'{0:.{1}f} km', 0),
    Unit(u'NM', 1 / 1852., u'{0:.{1}f} NM', 0),
    Unit(u'mi', 1 / 1609.34, u'{0:.{1}f} mi', 0),
)

speed_units = (
    Unit(u'm/s', 1, u'{0:.{1}f} m/s', 1),
    Unit(u'km/h', 3.6, u'{0:.{1}f} km/h', 1),
    Unit(u'kt', 1.94384449, u'{0:.{1}f} kt', 1),
    Unit(u'mph', 2.23693629, u'{0:.{1}f} mph', 1),
)

lift_units = (
    Unit(u'm/s', 1, u'{0:.{1}f} m/s', 1),
    Unit(u'kt', 1.94384449, u'{0:.{1}f} kt', 1),
    Unit(u'ft/min', 1 * 196.850394, u'{0:.{1}f} ft/min', 0),
)
altitude_units = (
    Unit(u'm', 1, u'{0:.{1}f} m', 0),
    Unit(u'ft', 1, u'{0:.{1}f} ft', 0)
)

unit_presets = (
    (l_("Custom"), {}),

    (l_("European (metric)"),
     {'distance_unit': u'km',
      'speed_unit': u'km/h',
      'lift_unit': u'm/s',
      'altitude_unit': u'm'
      }),

    (l_("British (imperial, distance in km)"),
     {'distance_unit': u'km',
      'speed_unit': u'kt',
      'lift_unit': u'kt',
      'altitude_unit': u'ft'
      }),

    (l_("Australian (metric, imperial height)"),
     {'distance_unit': u'km',
      'speed_unit': u'km/h',
      'lift_unit': u'kt',
      'altitude_unit': u'ft'
      }),

    (l_("American (imperial)"),
     {'distance_unit': u'mi',
      'speed_unit': u'kt',
      'lift_unit': u'kt',
      'altitude_unit': u'ft'
      }),
)


def unitid(options, name):
    return [x.name for x in options].index(name)


def _get_setting(name, default=None):
    if g.current_user:
        return getattr(g.current_user, name)
    else:
        return default


def get_setting_name(name):
    setting = _get_setting(name)

    if setting is None:
        return None

    if name == 'distance_unit' and distance_units[setting]:
        return distance_units[setting].name
    elif name == 'speed_unit' and speed_units[setting]:
        return speed_units[setting].name
    elif name == 'lift_unit' and lift_units[setting]:
        return lift_units[setting].name
    elif name == 'altitude_unit' and altitude_units[setting]:
        return altitude_units[setting].name

    return None


def _format(units, name, default, value, ndigits=None):
    assert isinstance(default, int)

    setting = _get_setting(name, default)
    if setting < 0 or setting >= len(units):
        setting = default

    if ndigits is None:
        ndigits = units[setting].decimal_places

    factor = units[setting].factor
    format = units[setting].format

    value = round(value * factor, ndigits)
    return format_decimal(value, format=format.format(0.0, ndigits))


def format_distance(value, ndigits=None):
    """Formats a distance value [m] to a user-readable string."""
    if value is None: return None

    return _format(distance_units, 'distance_unit', 1, value, ndigits)


def format_speed(value, ndigits=None):
    """Formats a speed value [m/s] to a user-readable string."""
    if value is None: return None

    return _format(speed_units, 'speed_unit', 1, value, ndigits)


def format_lift(value, ndigits=None):
    """Formats vertical speed value [m/s/] to a user-readable string"""
    if value is None: return None

    return _format(lift_units, 'lift_unit', 0, value, ndigits)


def format_altitude(value, ndigits=None):
    """Formats altitude value [m] to a user-readable string"""
    if value is None: return None

    return _format(altitude_units, 'altitude_unit', 0, value, ndigits)
