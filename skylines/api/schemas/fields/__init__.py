from collections import OrderedDict

from geoalchemy2.shape import to_shape
from marshmallow import fields, ValidationError
from shapely.geometry import Polygon, Point


class GeometryField(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return None

        shape = to_shape(value)
        if isinstance(shape, Point):
            return self.serialize_point(shape)
        if isinstance(shape, Polygon):
            return self.serialize_polygon(shape)

        raise ValidationError('Unknown shape type')

    @classmethod
    def serialize_polygon(cls, polygon):
        exterior = polygon.exterior
        if exterior is None:
            return None

        return map(cls.serialize_coord, exterior.coords)

    @classmethod
    def serialize_point(cls, point):
        return cls.serialize_coord(point.coords[0])

    @staticmethod
    def serialize_coord(coord):
        return OrderedDict([('longitude', coord[0]), ('latitude', coord[1])])
