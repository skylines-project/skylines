from collections import OrderedDict

from geoalchemy2.shape import to_shape
from marshmallow import Schema as _Schema, fields, post_dump, ValidationError
from shapely.geometry import Polygon, Point


class Schema(_Schema):
    class Meta:
        ordered = True


def replace_keywords(data):
    return OrderedDict(map(strip_underscore, data.iteritems()))


def strip_underscore(kv):
    k, v = kv
    if k.startswith('_'):
        k = k[1:]

    return k, v


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


class AirspaceSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    _class = fields.String(attribute='airspace_class')
    top = fields.String()
    base = fields.String()
    shape = GeometryField(attribute='the_geom')
    country = fields.String(attribute='country_code')
    created_at = fields.DateTime(attribute='time_created')
    modified_at = fields.DateTime(attribute='time_modified')

    @post_dump
    def replace_keywords(self, data):
        return replace_keywords(data)

airspace_list_schema = AirspaceSchema(only=('name', '_class', 'top', 'base', 'country'))


class AirportSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    short_name = fields.String()
    icao = fields.String()
    country = fields.String(attribute='country_code')
    elevation = fields.Float(attribute='altitude')
    location = GeometryField(attribute='location_wkt')
    type = fields.String()
    runways = fields.Function(lambda airport: [OrderedDict([
        ('length', airport.runway_len),
        ('direction', airport.runway_dir),
        ('surface', airport.surface),
    ])])
    frequencies = fields.Function(lambda airport: [OrderedDict([
        ('frequency', airport.frequency),
    ])])
    created_at = fields.DateTime(attribute='time_created')
    modified_at = fields.DateTime(attribute='time_modified')

airport_schema = AirportSchema()
airport_list_schema = AirportSchema(only=('id', 'name', 'elevation', 'location'))
