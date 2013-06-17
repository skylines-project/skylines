from flask import g
from flask.ext.babel import lazy_gettext as l_

from .numbers import format_decimal

distance_units = (
    (u'm', 1, u'{0:.{1}f} m', 0),
    (u'km', 1 / 1000., u'{0:.{1}f} km', 0),
    (u'NM', 1 / 1852., u'{0:.{1}f} NM', 0),
    (u'mi', 1 / 1609.34, u'{0:.{1}f} mi', 0),
)

speed_units = (
    (u'm/s', 1, u'{0:.{1}f} m/s', 1),
    (u'km/h', 3.6, u'{0:.{1}f} km/h', 1),
    (u'kt', 1.94384449, u'{0:.{1}f} kt', 1),
    (u'mph', 2.23693629, u'{0:.{1}f} mph', 1),
)

lift_units = (
    (u'm/s', 1, u'{0:.{1}f} m/s', 1),
    (u'kt', 1.94384449, u'{0:.{1}f} kt', 1),
    (u'ft/min', 1 * 196.850394, u'{0:.{1}f} ft/min', 0),
)
altitude_units = (
    (u'm', 1, u'{0:.{1}f} m', 0),
    (u'ft', 1, u'{0:.{1}f} ft', 0)
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
    return [x[0] for x in options].index(name)


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
        return distance_units[setting][0]
    elif name == 'speed_unit' and speed_units[setting]:
        return speed_units[setting][0]
    elif name == 'lift_unit' and lift_units[setting]:
        return lift_units[setting][0]
    elif name == 'altitude_unit' and altitude_units[setting]:
        return altitude_units[setting][0]

    return None


def _format(units, name, default, value, ndigits=None):
    assert isinstance(default, int)

    setting = _get_setting(name, default)
    if setting < 0 or setting >= len(units):
        setting = default

    if ndigits is None:
        ndigits = units[setting][3]

    factor = units[setting][1]
    format = units[setting][2]

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
