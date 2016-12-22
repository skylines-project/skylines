from skylines.schemas import Schema, fields


class AirspaceSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    _class = fields.String(attribute='airspace_class', dump_to='class')
    top = fields.String()
    base = fields.String()
    shape = fields.GeometryField(attribute='the_geom')
    country = fields.String(attribute='country_code')
    created_at = fields.DateTime(attribute='time_created')
    modified_at = fields.DateTime(attribute='time_modified')
