from marshmallow import Schema

from . import fields, validate


class ClubSchema(Schema):
    name = fields.String(required=True, strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))


class UserSchema(Schema):
    tracking_callsign = fields.String(load_from='trackingCallsign', strip=True, validate=validate.Length(max=5))
    tracking_delay = fields.Integer(load_from='trackingDelay', validate=validate.Range(min=0, max=60))
