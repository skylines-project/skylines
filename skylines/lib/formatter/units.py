from collections import namedtuple

from flask import g
from flask.ext.babel import lazy_gettext as l_

from .numbers import format_decimal

Unit = namedtuple('Unit', ['name', 'factor', 'format', 'decimal_places'])

DISTANCE_UNITS = (
    Unit(u'm', 1, u'{0:.{1}f}', 0),
    Unit(u'km', 1 / 1000., u'{0:.{1}f}', 0),
    Unit(u'NM', 1 / 1852., u'{0:.{1}f}', 0),
    Unit(u'mi', 1 / 1609.34, u'{0:.{1}f}', 0),
)

DEFAULT_DISTANCE_UNIT = 1

SPEED_UNITS = (
    Unit(u'm/s', 1, u'{0:.{1}f}', 1),
    Unit(u'km/h', 3.6, u'{0:.{1}f}', 1),
    Unit(u'kt', 1.94384449, u'{0:.{1}f}', 1),
    Unit(u'mph', 2.23693629, u'{0:.{1}f}', 1),
)

DEFAULT_SPEED_UNIT = 1

LIFT_UNITS = (
    Unit(u'm/s', 1, u'{0:.{1}f}', 1),
    Unit(u'kt', 1.94384449, u'{0:.{1}f}', 1),
    Unit(u'ft/min', 1 * 196.850394, u'{0:.{1}f}', 0),
)

DEFAULT_LIFT_UNIT = 0

ALTITUDE_UNITS = (
    Unit(u'm', 1, u'{0:.{1}f}', 0),
    Unit(u'ft', 3.280839895, u'{0:.{1}f}', 0)
)

DEFAULT_ALTITUDE_UNIT = 0

UNIT_PRESETS = (
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


def _get_setting(name, default=None, fallback_default=False):
    if g.current_user:
        return getattr(g.current_user, name)
    elif fallback_default:
        if name == 'distance_unit': return DEFAULT_DISTANCE_UNIT
        elif name == 'speed_unit': return DEFAULT_SPEED_UNIT
        elif name == 'lift_unit': return DEFAULT_LIFT_UNIT
        elif name == 'altitude_unit': return DEFAULT_ALTITUDE_UNIT
    else:
        return default


def get_setting_name(name, fallback=False):
    setting = _get_setting(name, fallback_default=fallback)

    if setting is None:
        return None

    if name == 'distance_unit' and DISTANCE_UNITS[setting]:
        return DISTANCE_UNITS[setting].name
    elif name == 'speed_unit' and SPEED_UNITS[setting]:
        return SPEED_UNITS[setting].name
    elif name == 'lift_unit' and LIFT_UNITS[setting]:
        return LIFT_UNITS[setting].name
    elif name == 'altitude_unit' and ALTITUDE_UNITS[setting]:
        return ALTITUDE_UNITS[setting].name

    return None


def _format(units, name, default, value, ndigits=None, add_name=True):
    assert isinstance(default, int)

    setting = _get_setting(name, default)
    if setting < 0 or setting >= len(units):
        setting = default

    if ndigits is None:
        ndigits = units[setting].decimal_places

    factor = units[setting].factor
    format = units[setting].format
    unit_name = units[setting].name

    value = round(float(value) * factor, ndigits)
    decimal = format_decimal(value, format=format.format(0.0, ndigits))

    if add_name:
        return decimal + ' ' + unit_name
    else:
        return decimal


def format_distance(value, ndigits=None, name=True):
    """Formats a distance value [m] to a user-readable string."""
    if value is None: return None

    return _format(DISTANCE_UNITS, 'distance_unit', DEFAULT_DISTANCE_UNIT,
                   value, ndigits, name)


def format_speed(value, ndigits=None, name=True):
    """Formats a speed value [m/s] to a user-readable string."""
    if value is None: return None

    return _format(SPEED_UNITS, 'speed_unit', DEFAULT_SPEED_UNIT,
                   value, ndigits, name)


def format_lift(value, ndigits=None, name=True):
    """Formats vertical speed value [m/s/] to a user-readable string"""
    if value is None: return None

    return _format(LIFT_UNITS, 'lift_unit', DEFAULT_LIFT_UNIT,
                   value, ndigits, name)


def format_altitude(value, ndigits=None, name=True):
    """Formats altitude value [m] to a user-readable string"""
    if value is None: return None

    return _format(ALTITUDE_UNITS, 'altitude_unit', DEFAULT_ALTITUDE_UNIT,
                   value, ndigits, name)
