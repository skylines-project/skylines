# -*- coding: utf-8 -*-

from sqlalchemy import func
from sqlalchemy.sql.expression import cast
from geoalchemy2.elements import WKTElement
from geoalchemy2.types import Geometry, Geography
from geoalchemy2.shape import to_shape

from skylines.database import db
from skylines.lib.geo import geographic_distance


class Location(object):
    def __init__(self, latitude=None, longitude=None):
        self.latitude = latitude
        self.longitude = longitude

    def to_wkt(self):
        return 'POINT({0} {1})'.format(self.longitude, self.latitude)

    def to_wkt_element(self, srid=4326):
        if not srid:
            srid = -1

        return WKTElement(self.to_wkt(), srid=srid)

    def make_point(self, srid=4326):
        """
        :type srid: int or None
        """

        point = db.func.ST_MakePoint(self.longitude, self.latitude)
        if srid:
            point = db.func.ST_SetSRID(point, srid)
        return point

    @staticmethod
    def from_wkb(wkb):
        coords = to_shape(wkb)
        return Location(latitude=coords.y, longitude=coords.x)

    def normalize(self):
        self.longitude %= 360
        if self.longitude > 180:
            self.longitude -= 360

    def __str__(self):
        return self.to_wkt()

    @staticmethod
    def get_clustered_locations(location_column,
                                threshold_radius=1000, filter=None):
        """
        SELECT ST_Centroid(
            (ST_Dump(
                ST_Union(
                    ST_Buffer(
                        takeoff_location_wkt::geography, 1000
                    )::geometry
                )
            )
        ).geom) FROM flights WHERE pilot_id=31;
        """

        # Cast the takeoff_location_wkt column to Geography
        geography = cast(location_column, Geography)

        # Add a metric buffer zone around the locations
        buffer = cast(geography.ST_Buffer(threshold_radius), Geometry)

        # Join the locations into one MultiPolygon
        union = buffer.ST_Union()

        # Split the MultiPolygon into separate polygons
        dump = union.ST_Dump().geom

        # Calculate center points of each polygon
        locations = func.ST_Centroid(dump)

        query = db.session.query(locations.label('location'))

        if filter is not None:
            query = query.filter(filter)

        return [Location.from_wkb(row.location) for row in query]

    def geographic_distance(self, other):
        return geographic_distance(self, other)


class Bounds(object):
    def __init__(self, southwest, northeast):
        if not (isinstance(southwest, Location) and
                isinstance(northeast, Location)):
            raise ValueError('SW and NE must be Location instances.')

        if southwest.latitude > northeast.latitude:
            raise ValueError(
                'SW latitude must be smaller or equal to NE latitude.')

        self.southwest = southwest
        self.northeast = northeast

    @staticmethod
    def from_bbox_string(bbox):
        bbox = bbox.split(',')
        if len(bbox) != 4:
            raise ValueError(
                'BBox string needs to have exactly four components')

        bbox = map(float, bbox)

        sw = Location(latitude=bbox[1], longitude=bbox[0])
        ne = Location(latitude=bbox[3], longitude=bbox[2])
        return Bounds(sw, ne)

    def get_width(self):
        return (self.northeast.longitude - self.southwest.longitude) % 360

    def get_height(self):
        return self.northeast.latitude - self.southwest.latitude

    def get_size(self):
        return self.get_width() * self.get_height()

    def normalize(self):
        self.southwest.normalize()
        self.northeast.normalize()

    def make_box(self, srid=4326):
        box = db.func.ST_MakeBox2D(self.southwest.make_point(srid=None),
                                   self.northeast.make_point(srid=None))
        if srid:
            box = db.func.ST_SetSRID(box, srid)

        return box
