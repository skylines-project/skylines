from babel.numbers import format_number, format_decimal

def format_distance(value):
    """Formats a distance value [m] to a user-readable string."""
    if value is None: return None

    return format_number(int(value / 1000 + 0.5)) + u' km'

def format_speed(value):
    """Formats a speed value [m/s] to a user-readable string."""
    if value is None: return None

    return format_decimal(value * 3.6, format=u'0.00 km/h')
