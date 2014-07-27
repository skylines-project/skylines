# -*- coding: utf-8 -*-

import math

EARTH_RADIUS = 6367009
METERS_PER_DEGREE = 111319.0
FEET_PER_METER = 3.2808399


def geographic_distance(loc1, loc2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians,
                                 [loc1.latitude, loc1.longitude,
                                  loc2.latitude, loc2.longitude])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return EARTH_RADIUS * c
