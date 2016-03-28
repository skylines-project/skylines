from marshmallow import fields

from skylines.api.schemas.base import BaseSchema


class ClubSchema(BaseSchema):
    id = fields.Integer()
    name = fields.String()
    website = fields.String()
    owner = fields.Integer(attribute='owner_id')
    created_at = fields.DateTime(attribute='time_created')
