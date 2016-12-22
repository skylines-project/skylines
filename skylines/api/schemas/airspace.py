from marshmallow import post_dump

from skylines.api.schemas.base import replace_keywords
from skylines.schemas import Schema, fields


class AirspaceSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    _class = fields.String(attribute='airspace_class')
    top = fields.String()
    base = fields.String()
    shape = fields.GeometryField(attribute='the_geom')
    country = fields.String(attribute='country_code')
    created_at = fields.DateTime(attribute='time_created')
    modified_at = fields.DateTime(attribute='time_modified')

    @post_dump
    def replace_keywords(self, data):
        return replace_keywords(data)
