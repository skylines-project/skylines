# -*- coding: utf-8 -*-

import math

EARTH_RADIUS = 6367009
METERS_PER_DEGREE = 111319.0


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


def zoom_bounding_box(bbox, ratio):
    center_x = (bbox[0] + bbox[2]) / 2.
    center_y = (bbox[1] + bbox[3]) / 2.

    return [
        (bbox[0] - center_x) * ratio + center_x,
        (bbox[1] - center_y) * ratio + center_y,
        (bbox[2] - center_x) * ratio + center_x,
        (bbox[3] - center_y) * ratio + center_y]
