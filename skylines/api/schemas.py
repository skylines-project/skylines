from marshmallow import Schema as _Schema, fields


class Schema(_Schema):
    class Meta:
        ordered = True


class AirspaceSchema(Schema):
    name = fields.String()
    airspace_class = fields.String()
    top = fields.String()
    base = fields.String()
    country = fields.String(attribute='country_code')

airspace_list_schema = AirspaceSchema()
