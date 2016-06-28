from marshmallow import Schema

from . import fields, validate

from skylines.lib.formatter.units import DISTANCE_UNITS, SPEED_UNITS, LIFT_UNITS, ALTITUDE_UNITS


class AircraftModelSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, strip=True, validate=validate.Length(max=64))
    index = fields.Integer(attribute='dmst_index')


class ClubSchema(Schema):
    name = fields.String(required=True, strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))
    website = fields.URL()


class FlightSchema(Schema):
    timeCreated = fields.DateTime(attribute='time_created')
    pilotId = fields.Integer(attribute='pilot_id', allow_none=True)
    pilotName = fields.String(attribute='pilot_name', strip=True, validate=validate.Length(max=255))
    copilotId = fields.Integer(attribute='co_pilot_id', allow_none=True)
    copilotName = fields.String(attribute='co_pilot_name', strip=True, validate=validate.Length(max=255))
    modelId = fields.Integer(attribute='model_id', load_only=True, allow_none=True)
    model = fields.Nested(AircraftModelSchema, dump_only=True)
    registration = fields.String(strip=True, validate=validate.Length(max=32))
    competitionId = fields.String(attribute='competition_id', strip=True, validate=validate.Length(max=5))

    scoreDate = fields.Date(attribute='date_local')

    takeoffTime = fields.DateTime(attribute='takeoff_time')
    scoreStartTime = fields.DateTime(attribute='scoring_start_time')
    scoreEndTime = fields.DateTime(attribute='scoring_end_time')
    landingTime = fields.DateTime(attribute='landing_time')

    distance = fields.Integer(attribute='olc_classic_distance')
    triangleDistance = fields.Integer(attribute='olc_triangle_distance')
    score = fields.Float(attribute='olc_plus_score')


class IGCFileSchema(Schema):
    registration = fields.String(strip=True, validate=validate.Length(max=32))
    competitionId = fields.String(attribute='competition_id', strip=True, validate=validate.Length(max=5))
    model = fields.String(strip=True, validate=validate.Length(max=64))


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(attribute='email_address', validate=validate.Length(max=255))
    firstName = fields.String(attribute='first_name', strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))
    lastName = fields.String(attribute='last_name', strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))
    name = fields.String(dump_only=True)
    trackingCallsign = fields.String(attribute='tracking_callsign', strip=True, validate=validate.Length(max=5))
    trackingDelay = fields.Integer(attribute='tracking_delay', validate=validate.Range(min=0, max=60))
    distanceUnit = fields.Integer(attribute='distance_unit', validate=validate.Range(min=0, max=len(DISTANCE_UNITS) - 1))
    speedUnit = fields.Integer(attribute='speed_unit', validate=validate.Range(min=0, max=len(SPEED_UNITS) - 1))
    liftUnit = fields.Integer(attribute='lift_unit', validate=validate.Range(min=0, max=len(LIFT_UNITS) - 1))
    altitudeUnit = fields.Integer(attribute='altitude_unit', validate=validate.Range(min=0, max=len(ALTITUDE_UNITS) - 1))


class FlightCommentSchema(Schema):
    user = fields.Nested(UserSchema, only=('id', 'name'))
    text = fields.String(required=True)
