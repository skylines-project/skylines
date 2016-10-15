from collections import namedtuple

from flask import g

Unit = namedtuple('Unit', ['name', 'factor', 'format', 'decimal_places'])

DISTANCE_UNITS = (
    Unit(u'm', 1, u'{0:.{1}f}', 0),
    Unit(u'km', 1 / 1000., u'{0:.{1}f}', 0),
    Unit(u'NM', 1 / 1852., u'{0:.{1}f}', 0),
    Unit(u'mi', 1 / 1609.34, u'{0:.{1}f}', 0),
)

SPEED_UNITS = (
    Unit(u'm/s', 1, u'{0:.{1}f}', 1),
    Unit(u'km/h', 3.6, u'{0:.{1}f}', 1),
    Unit(u'kt', 1.94384449, u'{0:.{1}f}', 1),
    Unit(u'mph', 2.23693629, u'{0:.{1}f}', 1),
)

LIFT_UNITS = (
    Unit(u'm/s', 1, u'{0:.{1}f}', 1),
    Unit(u'kt', 1.94384449, u'{0:.{1}f}', 1),
    Unit(u'ft/min', 1 * 196.850394, u'{0:.{1}f}', 0),
)

ALTITUDE_UNITS = (
    Unit(u'm', 1, u'{0:.{1}f}', 0),
    Unit(u'ft', 3.280839895, u'{0:.{1}f}', 0)
)


def _get_setting(name, default=None):
    return getattr(g.current_user, name) if g.current_user else default


def get_setting_name(name):
    setting = _get_setting(name)

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
