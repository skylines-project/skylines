from datetime import datetime, timedelta
from math import log

from flask import Blueprint, request, abort
from sqlalchemy.sql.expression import and_

from skylines.api.json import jsonify
from skylines.api.cache import cache
from skylines.api.oauth import oauth
from skylines.lib.dbutil import get_requested_record_list, get_requested_record
from skylines.lib.decorators import jsonp
from skylines.lib.helpers import color
from skylines.lib.xcsoar_ import FlightPathFix
from skylines.lib.geoid import egm96_height
from skylines.model import TrackingFix, Airport, Follower, User, Location
from skylines.schemas import TrackingFixSchema, AirportSchema, UserSchema
import xcsoar

UNKNOWN_ELEVATION = -1000

tracking_blueprint = Blueprint('tracking', 'skylines')


# Use `live` alias here since `/api/tracking/*` is filtered by the "EasyPrivacy" adblocker list...
@tracking_blueprint.route('/tracking', strict_slashes=False)
@tracking_blueprint.route('/live', strict_slashes=False)
@oauth.optional()
def index():
    fix_schema = TrackingFixSchema(only=('time', 'location', 'altitude', 'elevation', 'pilot'))
    airport_schema = AirportSchema(only=('id', 'name', 'countryCode'))

    @cache.memoize(timeout=(60 * 60))
    def get_nearest_airport(track):
        airport = Airport.by_location(track.location, None)
        if not airport:
            return None

        return dict(airport=airport_schema.dump(airport).data,
                    distance=airport.distance(track.location))

    tracks = []
    for t in TrackingFix.get_latest():
        nearest_airport = get_nearest_airport(t)

        track = fix_schema.dump(t).data
        if nearest_airport:
            track['nearestAirport'] = nearest_airport['airport']
            track['nearestAirportDistance'] = nearest_airport['distance']

        tracks.append(track)

    if request.user_id:
        followers = [f.destination_id for f in Follower.query(source_id=request.user_id)]
    else:
        followers = []

    return jsonify(friends=followers, tracks=tracks)


@tracking_blueprint.route('/tracking/latest.json')
@jsonp
def latest():
    fixes = []
    for fix in TrackingFix.get_latest():
        json = dict(time=fix.time.isoformat() + 'Z',
                    location=fix.location.to_wkt(),
                    pilot=dict(id=fix.pilot_id, name=unicode(fix.pilot)))

        optional_attributes = ['track', 'ground_speed', 'airspeed',
                               'altitude', 'vario', 'engine_noise_level']
        for attr in optional_attributes:
            value = getattr(fix, attr)
            if value is not None:
                json[attr] = value

        fixes.append(json)

    return jsonify(fixes=fixes)


@tracking_blueprint.route('/tracking/<user_ids>', strict_slashes=False)
@tracking_blueprint.route('/live/<user_ids>', strict_slashes=False)
def read(user_ids):
    pilots = get_requested_record_list(User, user_ids, joinedload=[User.club])

    color_gen = color.generator()
    for pilot in pilots:
        pilot.color = color_gen.next()

    traces = map(_get_flight_path, pilots)
    if not any(traces):
        traces = None

    user_schema = UserSchema()

    pilots_json = []
    for pilot in pilots:
        json = user_schema.dump(pilot).data
        json['color'] = pilot.color
        pilots_json.append(json)

    flights = []
    if traces:
        for pilot, trace in zip(pilots, traces):
            if trace:
                flights.append({
                    'sfid': pilot.id,
                    'points': trace['points'],
                    'barogram_t': trace['barogram_t'],
                    'barogram_h': trace['barogram_h'],
                    'enl': trace['enl'],
                    'contests': None,
                    'elevations_t': trace['barogram_t'],
                    'elevations_h': trace['elevations'],
                    'geoid': trace['geoid'],
                    'additional': {
                        'competition_id': pilot.tracking_callsign or pilot.initials(),
                        'color': pilot.color,
                    },
                })

    return jsonify(flights=flights, pilots=pilots_json)


@tracking_blueprint.route('/tracking/<user_id>/json')
@tracking_blueprint.route('/live/<user_id>/json')
def json(user_id):
    pilot = get_requested_record(User, user_id, joinedload=[User.club])
    last_update = request.values.get('last_update', 0, type=int)

    trace = _get_flight_path(pilot, threshold=0.001, last_update=last_update)
    if not trace:
        abort(404)

    return jsonify(
        points=trace['points'],
        barogram_t=trace['barogram_t'],
        barogram_h=trace['barogram_h'],
        elevations=trace['elevations'],
        enl=trace['enl'],
        geoid=trace['geoid'],
        sfid=pilot.id)


def _get_flight_path(pilot, threshold=0.001, last_update=None):
    fp = _get_flight_path2(pilot, last_update=last_update)
    if not fp:
        return None

    num_levels = 4
    zoom_factor = 4
    zoom_levels = [0]
    zoom_levels.extend([round(-log(32.0 / 45.0 * (threshold * pow(zoom_factor, num_levels - i - 1)), 2)) for i in range(1, num_levels)])

    xcsoar_flight = xcsoar.Flight(fp)

    xcsoar_flight.reduce(num_levels=num_levels,
                         zoom_factor=zoom_factor,
                         threshold=threshold)

    encoded_flight = xcsoar_flight.encode()

    points = encoded_flight['locations']
    barogram_t = encoded_flight['times']
    barogram_h = encoded_flight['altitude']
    enl = encoded_flight['enl']

    fp_reduced = map(lambda line: FlightPathFix(*line), xcsoar_flight.path())
    elevations = xcsoar.encode([fix.elevation if fix.elevation is not None else UNKNOWN_ELEVATION for fix in fp_reduced], method="signed")

    geoid_height = egm96_height(Location(latitude=fp[0].location['latitude'],
                                         longitude=fp[0].location['longitude']))

    return dict(points=points,
                barogram_t=barogram_t, barogram_h=barogram_h, enl=enl,
                elevations=elevations, geoid=geoid_height)


def _get_flight_path2(pilot, last_update=None):
    query = TrackingFix.query() \
        .filter(and_(TrackingFix.pilot == pilot,
                     TrackingFix.location != None,
                     TrackingFix.altitude != None,
                     TrackingFix.max_age_filter(12),
                     TrackingFix.time_visible <= datetime.utcnow()))

    query = query.order_by(TrackingFix.time)

    start_fix = query.first()

    if not start_fix:
        return None

    start_time = start_fix.time.hour * 3600 + start_fix.time.minute * 60 + start_fix.time.second

    if last_update:
        query = query.filter(TrackingFix.time >= start_fix.time +
                             timedelta(seconds=(last_update - start_time)))

    result = []
    for fix in query:
        location = fix.location
        if location is None:
            continue

        time_delta = fix.time - start_fix.time
        time = start_time + time_delta.days * 86400 + time_delta.seconds

        result.append(FlightPathFix(datetime=fix.time,
                                    seconds_of_day=time,
                                    location={'latitude': location.latitude,
                                              'longitude': location.longitude},
                                    gps_altitude=fix.altitude,
                                    enl=fix.engine_noise_level,
                                    track=fix.track,
                                    groundspeed=fix.ground_speed,
                                    tas=fix.airspeed,
                                    elevation=fix.elevation))

    return result
