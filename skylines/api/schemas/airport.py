from collections import OrderedDict

from marshmallow import fields

from skylines.api.schemas.base import BaseSchema
from skylines.api.schemas.fields.geo import GeometryField


class AirportSchema(BaseSchema):
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
