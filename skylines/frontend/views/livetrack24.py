from datetime import datetime

from flask import Blueprint, request
from werkzeug.exceptions import BadRequest, NotFound, NotImplemented

from skylines.database import db
from skylines.model import User, TrackingFix, TrackingSession, Elevation

lt24_blueprint = Blueprint('lt24', 'skylines')


def _parse_user():
    """Read and check the tracking key (supplied via 'user' field)"""

    if 'user' not in request.values:
        raise BadRequest('`user` parameter is missing.')

    try:
        key = int(request.values['user'], 16)
    except ValueError:
        raise BadRequest('`user` must be the hexadecimal tracking key.')

    return key, User.by_tracking_key(key)


def _parse_session_id():
    """Read and check the session id"""

    if 'sid' not in request.values:
        raise BadRequest('`sid` parameter is missing.')

    try:
        session_id = int(request.values['sid'])
    except ValueError:
        raise BadRequest('`sid` must be an integer.')

    if session_id & 0x80000000 == 0:
        raise NotImplemented('Unregistered users are not supported.')

    return session_id


def _parse_fix(pilot_id):
    fix = TrackingFix()
    fix.ip = request.remote_addr
    fix.pilot_id = pilot_id

    # Time
    if 'tm' not in request.values:
        raise BadRequest('`tm` (time) parameter is missing.')

    try:
        fix.time = datetime.utcfromtimestamp(int(request.values['tm']))
    except ValueError:
        raise BadRequest('`tm` (time) has to be a POSIX timestamp.')

    # Location
    if 'lat' in request.values and 'lon' in request.values:
        try:
            fix.set_location(float(request.values['lon']), float(request.values['lat']))
        except ValueError:
            raise BadRequest('`lat` and `lon` have to be floating point value in degrees (WGS84).')

    # Altitude
    if 'alt' in request.values:
        try:
            fix.altitude = int(request.values['alt'])
        except ValueError:
            raise BadRequest('`alt` has to be an integer value in meters.')

        if not -1000 <= fix.altitude <= 15000:
            raise BadRequest('`alt` has to be a valid altitude in the range of -1000 to 15000 meters.')

    # Speed
    if 'sog' in request.values:
        try:
            fix.ground_speed = int(request.values['sog']) / 3.6
        except ValueError:
            raise BadRequest('`sog` (speed over ground) has to be an integer value in km/h.')

        if not 0 <= fix.ground_speed <= (500 / 3.6):
            raise BadRequest('`sog` (speed over ground) has to be a valid speed in the range of 0 to 500 km/h.')

    # Track
    if 'cog' in request.values:
        try:
            fix.track = int(request.values['cog'])
        except ValueError:
            raise BadRequest('`cog` (course over ground) has to be an integer value in degrees.')

        if not 0 <= fix.track < 360:
            raise BadRequest('`cog` (course over ground) has to be a valid angle between 0 and 360 degrees.')

    fix.elevation = Elevation.get(fix.location_wkt)

    return fix


def _sessionless_fix():
    key, pilot = _parse_user()
    if not pilot:
        raise NotFound('No pilot found with tracking key `{:X}`.'.format(key))

    fix = _parse_fix(pilot.id)
    db.session.add(fix)
    db.session.commit()
    return 'OK'


def _session_fix():
    session_id = _parse_session_id()
    session = TrackingSession.by_lt24_id(session_id)
    if session is None:
        raise NotFound('No open tracking session found with id `{:d}`.'.format(session_id))

    fix = _parse_fix(session.pilot_id)
    db.session.add(fix)
    db.session.commit()
    return 'OK'


def _create_session():
    key, pilot = _parse_user()
    if not pilot:
        raise NotFound('No pilot found with tracking key `{:X}`.'.format(key))

    session_id = _parse_session_id()

    if session_id & 0x00FFFFFF != key & 0x00FFFFFF:
        raise BadRequest('The right three bytes must match the userid (tracking key).')

    session = TrackingSession()
    session.pilot = pilot
    session.lt24_id = session_id
    session.ip_created = request.remote_addr

    # Client application
    if 'client' in request.values:
        session.client = request.values['client'][:32]
    if 'v' in request.values:
        session.client_version = request.values['v'][:8]

    # Device information
    if 'phone' in request.values:
        session.device = request.values['phone'][:32]
    if 'gps' in request.values:
        session.gps_device = request.values['gps'][:32]

    # Aircraft model and type
    if 'vname' in request.values:
        session.aircraft_model = request.values['vname'][:64]
    if 'vtype' in request.values:
        try:
            session.aircraft_type = int(request.values['vtype'])
        except ValueError:
            raise BadRequest('`vtype` has to be a valid integer.')

    db.session.add(session)
    db.session.commit()
    return 'OK'


def _finish_session():
    session_id = _parse_session_id()
    session = TrackingSession.by_lt24_id(session_id)
    if session is None:
        raise NotFound('No open tracking session found with id `{:d}`.'.format(session_id))

    session.time_finished = datetime.utcnow()
    session.ip_finished = request.remote_addr

    # Pilot status
    if 'prid' in request.values:
        try:
            finish_status = int(request.values['prid'])
            if not (0 <= finish_status <= 4):
                raise ValueError()

            session.finish_status = finish_status

        except ValueError:
            raise BadRequest('`prid` must be an integer between 0 and 4.')

    db.session.commit()
    return 'OK'


@lt24_blueprint.route('/track.php', methods=['GET', 'POST'])
def track():
    """
    LiveTrack24 tracking API

    see: http://www.livetrack24.com/wiki/LiveTracking%20API
    """

    # Read and check the request type

    if 'leolive' not in request.values:
        raise BadRequest('`leolive` parameter is missing.')

    leolive = request.values.get('leolive', 0, type=int)
    if not (1 <= leolive <= 4):
        raise BadRequest('`leolive` must be an integer between 1 and 4.')

    if leolive == 1:
        return _sessionless_fix()
    elif leolive == 2:
        return _create_session()
    elif leolive == 3:
        return _finish_session()
    elif leolive == 4:
        return _session_fix()


@lt24_blueprint.route('/client.php', methods=['GET', 'POST'])
def client():
    """
    LiveTrack24 tracking API

    see: http://www.livetrack24.com/wiki/LiveTracking%20API
    """

    # Read and check the request type

    if 'op' not in request.values:
        raise BadRequest('`op` parameter is missing.')

    if request.values['op'] != 'login':
        raise BadRequest('`op` parameter has to be `login`.')

    # Read and check the tracking key (supplied via 'user' field)

    key, pilot = _parse_user()
    if not pilot:
        return '0'

    return '{:d}'.format(key)
