from marshmallow import Schema

from . import fields, validate

from skylines.lib.formatter.units import DISTANCE_UNITS, SPEED_UNITS, LIFT_UNITS, ALTITUDE_UNITS


class ClubSchema(Schema):
    name = fields.String(required=True, strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))


class UserSchema(Schema):
    email_address = fields.Email(load_from='email', validate=validate.Length(max=255))
    first_name = fields.String(load_from='firstName', strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))
    last_name = fields.String(load_from='lastName', strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))
    tracking_callsign = fields.String(load_from='trackingCallsign', strip=True, validate=validate.Length(max=5))
    tracking_delay = fields.Integer(load_from='trackingDelay', validate=validate.Range(min=0, max=60))
    distance_unit = fields.Integer(load_from='distanceUnit', validate=validate.Range(min=0, max=len(DISTANCE_UNITS) - 1))
    speed_unit = fields.Integer(load_from='speedUnit', validate=validate.Range(min=0, max=len(SPEED_UNITS) - 1))
    lift_unit = fields.Integer(load_from='liftUnit', validate=validate.Range(min=0, max=len(LIFT_UNITS) - 1))
    altitude_unit = fields.Integer(load_from='altitudeUnit', validate=validate.Range(min=0, max=len(ALTITUDE_UNITS) - 1))
