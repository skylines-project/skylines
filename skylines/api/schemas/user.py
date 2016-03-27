from marshmallow import fields

from skylines.api.schemas.base import BaseSchema


class UserSchema(BaseSchema):
    id = fields.Integer()
    name = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    club = fields.Integer(attribute='club_id')
    tracking_delay = fields.Integer()
    tracking_call_sign = fields.String(attribute='tracking_callsign')
    created_at = fields.DateTime(attribute='created')


class AuthenticatedUserSchema(UserSchema):
    email = fields.Email(attribute='email_address')
    tracking_key = fields.String(attribute='tracking_key_hex')
    admin = fields.Bool()
