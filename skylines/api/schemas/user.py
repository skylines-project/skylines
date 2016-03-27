from marshmallow import fields

from skylines.api.schemas.base import BaseSchema


class UserSchema(BaseSchema):
    id = fields.Integer()
    email = fields.Email(attribute='email_address')
    name = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    club = fields.Integer(attribute='club_id')
    tracking_delay = fields.Integer()
    tracking_call_sign = fields.String(attribute='tracking_callsign')

    # only for the authenticated user
    tracking_key = fields.String(attribute='tracking_key_hex')
    created_at = fields.DateTime(attribute='created')
    admin = fields.Bool()
