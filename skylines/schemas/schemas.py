from marshmallow import Schema as _Schema

from . import fields, validate

from skylines.lib.formatter.units import DISTANCE_UNITS, SPEED_UNITS, LIFT_UNITS, ALTITUDE_UNITS

AIRCRAFT_MODEL_TYPES = {
    1: 'glider',
    2: 'motorglider',
    3: 'paraglider',
    4: 'hangglider',
    5: 'ul',
}


class Schema(_Schema):
    # Set `strict=True` as default for our schemas
    def __init__(self, strict=True, *args, **kwargs):
        super(Schema, self).__init__(strict=strict, *args, **kwargs)


class AircraftModelSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, strip=True, validate=validate.Length(max=64))
    index = fields.Integer(attribute='dmst_index')
    type = fields.Method('get_type')

    def get_type(self, obj):
        return AIRCRAFT_MODEL_TYPES[obj.kind]


class AirportSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, strip=True, validate=validate.Length(max=255))
    countryCode = fields.String(attribute='country_code', dump_only=True)


class AirspaceSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    type = fields.String(attribute='airspace_class')
    base = fields.String()
    top = fields.String()
    countryCode = fields.String(attribute='country_code')


class ClubSchema(Schema):
    id = fields.Integer(dump_only=True)
    timeCreated = fields.DateTime(attribute='time_created')

    name = fields.String(required=True, strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))
    website = fields.String(validate=validate.URL())

    owner = fields.Nested('skylines.schemas.schemas.UserSchema', only=('id', 'name'), dump_only=True)


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.String(attribute='email_address', required=True, validate=(
        validate.Email(),
        validate.Length(max=255),
    ))
    firstName = fields.String(attribute='first_name', required=True, strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))
    lastName = fields.String(attribute='last_name', required=True, strip=True, validate=(
        validate.NotEmpty(),
        validate.Length(min=1, max=255),
    ))
    name = fields.String(dump_only=True)

    clubId = fields.Integer(attribute='club_id', allow_none=True)
    club = fields.Nested(ClubSchema, only=('id', 'name'))

    trackingCallsign = fields.String(attribute='tracking_callsign', strip=True, validate=validate.Length(max=5))
    trackingDelay = fields.Integer(attribute='tracking_delay', validate=validate.Range(min=0, max=60))

    class Meta:
        load_only = ('clubId',)
        dump_only = ('club',)


class CurrentUserSchema(UserSchema):
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6))
    currentPassword = fields.String(load_only=True)

    recoveryKey = fields.String(attribute='recover_key', required=True, load_only=True,
                                validate=validate.Regexp('^[\da-fA-F]+$'))

    trackingKey = fields.String(attribute='tracking_key_hex', dump_only=True)

    distanceUnit = fields.Integer(attribute='distance_unit', validate=validate.Range(min=0, max=len(DISTANCE_UNITS) - 1))
    speedUnit = fields.Integer(attribute='speed_unit', validate=validate.Range(min=0, max=len(SPEED_UNITS) - 1))
    liftUnit = fields.Integer(attribute='lift_unit', validate=validate.Range(min=0, max=len(LIFT_UNITS) - 1))
    altitudeUnit = fields.Integer(attribute='altitude_unit', validate=validate.Range(min=0, max=len(ALTITUDE_UNITS) - 1))


class IGCFileSchema(Schema):
    ownerId = fields.Integer(attribute='owner_id')
    owner = fields.Nested(UserSchema, only=('id', 'name'))

    filename = fields.String(strip=True)

    registration = fields.String(strip=True, validate=validate.Length(max=32))
    competitionId = fields.String(attribute='competition_id', strip=True, validate=validate.Length(max=5))
    model = fields.String(strip=True, validate=validate.Length(max=64))

    date = fields.Date(attribute='date_utc')

    class Meta:
        load_only = ('ownerId',)
        dump_only = ('owner',)


class FlightSchema(Schema):
    id = fields.Integer()
    timeCreated = fields.DateTime(attribute='time_created')

    pilotId = fields.Integer(attribute='pilot_id', allow_none=True)
    pilot = fields.Nested(UserSchema, only=('id', 'name'))
    pilotName = fields.String(attribute='pilot_name', strip=True, allow_none=True, validate=validate.Length(max=255))

    copilotId = fields.Integer(attribute='co_pilot_id', allow_none=True)
    copilot = fields.Nested(UserSchema, attribute='co_pilot', only=('id', 'name'))
    copilotName = fields.String(attribute='co_pilot_name', strip=True, allow_none=True, validate=validate.Length(max=255))

    clubId = fields.Integer(attribute='club_id', allow_none=True)
    club = fields.Nested(ClubSchema, only=('id', 'name'))

    modelId = fields.Integer(attribute='model_id', allow_none=True)
    model = fields.Nested(AircraftModelSchema)
    registration = fields.String(allow_none=True, strip=True, validate=validate.Length(max=32))
    competitionId = fields.String(attribute='competition_id', allow_none=True, strip=True, validate=validate.Length(max=5))

    scoreDate = fields.Date(attribute='date_local')

    takeoffTime = fields.DateTime(attribute='takeoff_time')
    scoreStartTime = fields.DateTime(attribute='scoring_start_time')
    scoreEndTime = fields.DateTime(attribute='scoring_end_time')
    landingTime = fields.DateTime(attribute='landing_time')

    takeoffAirportId = fields.Integer(attribute='takeoff_airport_id', allow_none=True)
    takeoffAirport = fields.Nested(AirportSchema, attribute='takeoff_airport', only=('id', 'name', 'countryCode'))

    landingAirportId = fields.Integer(attribute='landing_airport_id', allow_none=True)
    landingAirport = fields.Nested(AirportSchema, attribute='landing_airport', only=('id', 'name', 'countryCode'))

    distance = fields.Integer(attribute='olc_classic_distance')
    triangleDistance = fields.Integer(attribute='olc_triangle_distance')
    rawScore = fields.Float(attribute='olc_plus_score')
    score = fields.Float(attribute='index_score')
    speed = fields.Float()

    igcFile = fields.Nested(IGCFileSchema, attribute='igc_file', only=(
        'owner', 'filename', 'registration', 'competitionId', 'model', 'date'))

    class Meta:
        load_only = ('pilotId', 'copilotId', 'clubId', 'modelId', 'takeoffAirportId', 'landingAirportId')
        dump_only = ('pilot', 'copilot', 'club', 'model', 'takeoffAirport', 'landingAirport', 'speed', 'score', 'igcFile')


class FlightCommentSchema(Schema):
    user = fields.Nested(UserSchema, only=('id', 'name'))
    text = fields.String(required=True)


class TrackingFixSchema(Schema):
    time = fields.DateTime()
    location = fields.Location()
    altitude = fields.Integer()
    elevation = fields.Integer()

    pilot = fields.Nested(UserSchema, only=('id', 'name'))
