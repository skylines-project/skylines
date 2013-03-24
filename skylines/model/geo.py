# -*- coding: utf-8 -*-
import re
from sqlalchemy import func
from sqlalchemy.sql.expression import cast
from geoalchemy2.types import Geometry, Geography
from geoalchemy2.shape import to_shape
from skylines.model.session import DBSession
from skylines.lib.sql import extract_field

wkt_re = re.compile(r'POINT\(([\+\-\d.]+) ([\+\-\d.]+)\)')


class Location(object):
    def __init__(self, latitude=None, longitude=None):
        self.latitude = latitude
        self.longitude = longitude

    def to_wkt(self):
        return 'POINT({0} {1})'.format(self.longitude, self.latitude)

    @staticmethod
    def from_wkt(wkt):
        match = wkt_re.match(wkt)
        if not match:
            return None

        return Location(latitude=float(match.group(2)),
                        longitude=float(match.group(1)))

    @staticmethod
    def from_wkb(wkb):
        coords = to_shape(wkb).coords[0]
        return Location(latitude=coords[1], longitude=coords[0])

    def __str__(self):
        return self.to_wkt()

    @staticmethod
    def get_clustered_locations(location_column,
                                threshold_radius=1000, filter=None):
        '''
        SELECT ST_AsText(
            ST_Centroid(
                (ST_Dump(
                    ST_Union(
                        ST_Buffer(
                            takeoff_location_wkt::geography, 1000
                        )::geometry
                    )
                )
            ).geom)
        ) FROM flights WHERE pilot_id=31;
        '''

        # Cast the takeoff_location_wkt column to Geography
        geography = cast(location_column, Geography)

        # Add a metric buffer zone around the locations
        buffer = cast(func.ST_Buffer(geography, threshold_radius), Geometry)

        # Join the locations into one MultiPolygon
        union = func.ST_Union(buffer)

        # Split the MultiPolygon into separate polygons
        dump = extract_field(func.ST_Dump(union), 'geom')

        # Calculate center points of each polygon
        locations = func.ST_Centroid(dump)

        # Convert the result into WKT
        locations = func.ST_AsText(locations)

        query = DBSession.query(locations.label('location'))

        if filter is not None:
            query = query.filter(filter)

        return [Location.from_wkt(row.location) for row in query]
