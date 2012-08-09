from babel.numbers import format_number, format_decimal
from tg import request

distance_units = (
    (u'm', lambda value: format_number(int(value)) + u' m'),
    (u'km', lambda value: format_number(int(value / 1000. + 0.5)) + u' km'),
    (u'NM', lambda value: format_number(int(value / 1852. + 0.5)) + u' NM'),
    (u'mi', lambda value: format_number(int(value / 1609.34 + 0.5)) + u' mi'),
)

speed_units = (
    (u'm/s', lambda value: format_decimal(value, format=u'0.00 m/s')),
    (u'km/h', lambda value: format_decimal(value * 3.6, format=u'0.00 km/h')),
    (u'kt', lambda value: format_decimal(value * 1.94384449, format=u'0.00 kt')),
    (u'mph', lambda value: format_decimal(value * 2.23693629, format=u'0.00 mph')),
)

lift_units = (
    (u'm/s', lambda value: format_decimal(value, format=u'0.00 m/s')),
    (u'kt', lambda value: format_decimal(value * 1.94384449, format=u'0.00 kt')),
    (u'ft/min', lambda value: format_decimal(value * 196.850394,
                                             format=u'0.00 ft/min')),
)
altitude_units = (
    (u'm', lambda value: "%d m" % value),
    (u'ft', lambda value: "%d ft" % (value * 3.2808399))
)

unit_presets = (
    ("Custom", {}),

    ("European (metric)",
     {'distance_unit': u'km',
      'speed_unit': u'km/h',
      'lift_unit': u'm/s',
      'altitude_unit': u'm'
      }),

    ("British (imperial, distance in km)",
     {'distance_unit': u'km',
      'speed_unit': u'kt',
      'lift_unit': u'kt',
      'altitude_unit': u'ft'
      }),

    ("American (imperial)",
     {'distance_unit': u'mi',
      'speed_unit': u'kt',
      'lift_unit': u'kt',
      'altitude_unit': u'ft'
      }),
 )


def unitid(options, name):
    return [x[0] for x in options].index(name)

def _get_setting(name, default=None):
    if request.identity:
        return getattr(request.identity['user'], name)
    else:
        return default

def _format(units, name, default, value):
    assert isinstance(default, int)

    setting = _get_setting(name, default)
    if setting < 0 or setting >= len(units):
        setting = default
    return units[setting][1](value)

def format_distance(value):
    """Formats a distance value [m] to a user-readable string."""
    if value is None: return None

    return _format(distance_units, 'distance_unit', 1, value)

def format_speed(value):
    """Formats a speed value [m/s] to a user-readable string."""
    if value is None: return None

    return _format(speed_units, 'speed_unit', 1, value)

def format_lift(value):
    """Formats vertical speed value [m/s/] to a user-readable string"""
    if value is None: return None

    return _format(lift_units, 'lift_unit', 0, value)

def format_altitude(value):
    """Formats altitude value [m] to a user-readable string"""
    if value is None: return None

    return _format(altitude_units, 'altitude_unit', 0, value)
