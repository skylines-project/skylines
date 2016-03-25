from marshmallow import fields

from skylines.api.schemas.base import BaseSchema


class UserSchema(BaseSchema):
    id = fields.Integer()
    name = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    email_address = fields.Email()
    tracking_key = fields.Integer()
    tracking_delay = fields.Integer()
    tracking_call_sign = fields.String(attribute='tracking_callsign')
    created_at = fields.DateTime(attribute='created')
