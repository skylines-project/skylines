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
