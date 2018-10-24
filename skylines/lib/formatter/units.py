from collections import namedtuple

Unit = namedtuple("Unit", ["name", "factor", "format", "decimal_places"])

DISTANCE_UNITS = (
    Unit(u"m", 1, u"{0:.{1}f}", 0),
    Unit(u"km", 1 / 1000.0, u"{0:.{1}f}", 0),
    Unit(u"NM", 1 / 1852.0, u"{0:.{1}f}", 0),
    Unit(u"mi", 1 / 1609.34, u"{0:.{1}f}", 0),
)

SPEED_UNITS = (
    Unit(u"m/s", 1, u"{0:.{1}f}", 1),
    Unit(u"km/h", 3.6, u"{0:.{1}f}", 1),
    Unit(u"kt", 1.94384449, u"{0:.{1}f}", 1),
    Unit(u"mph", 2.23693629, u"{0:.{1}f}", 1),
)

LIFT_UNITS = (
    Unit(u"m/s", 1, u"{0:.{1}f}", 1),
    Unit(u"kt", 1.94384449, u"{0:.{1}f}", 1),
    Unit(u"ft/min", 1 * 196.850394, u"{0:.{1}f}", 0),
)

ALTITUDE_UNITS = (
    Unit(u"m", 1, u"{0:.{1}f}", 0),
    Unit(u"ft", 3.280839895, u"{0:.{1}f}", 0),
)
