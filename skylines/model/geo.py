# -*- coding: utf-8 -*-
import re

wkt_re = re.compile(r'POINT\(([\+\-\d.]+) ([\+\-\d.]+)\)')


class Location(object):
    def __init__(self, latitude = None, longitude = None):
        self.latitude = latitude
        self.longitude = longitude

    def to_wkt(self):
        return 'POINT({0} {1})'.format(self.longitude, self.latitude)

    @staticmethod
    def from_wkt(wkt):
        match = wkt_re.match(wkt)
        if not match:
            return None

        return Location(latitude = float(match.group(2)), 
                        longitude = float(match.group(1)))
