from marshmallow import ValidationError
from marshmallow.fields import *  # NOQA
from marshmallow.fields import Field
from marshmallow.fields import String as _String

from geoalchemy2.shape import to_shape
from shapely.geometry import Polygon, Point


class String(_String):
    def __init__(self, strip=False, *args, **kwargs):
        super(String, self).__init__(*args, **kwargs)
        self.strip = strip

    def _deserialize(self, value, attr, data):
        value = super(String, self)._deserialize(value, attr, data)

        if self.strip:
            value = value.strip()

        return value


class Location(Field):
    def _serialize(self, value, attr, obj):
        return value.to_lonlat() if value else None


class GeometryField(Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return None

        shape = to_shape(value)
        if isinstance(shape, Point):
            return self.serialize_point(shape)
        if isinstance(shape, Polygon):
            return self.serialize_polygon(shape)

        raise ValidationError("Unsupported shape type")

    @classmethod
    def serialize_polygon(cls, polygon):
        exterior = polygon.exterior
        if exterior is None:
            return None

        return list(map(cls.serialize_coord, exterior.coords))

    @classmethod
    def serialize_point(cls, point):
        return cls.serialize_coord(point.coords[0])

    @staticmethod
    def serialize_coord(coord):
        return [coord[0], coord[1]]


# Aliases
Str = String
