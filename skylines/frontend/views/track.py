from datetime import timedelta
from math import log

from flask import Blueprint, request, render_template, abort, jsonify, g
from sqlalchemy.sql.expression import and_

from skylines.lib.dbutil import get_requested_record_list
from skylines.lib.helpers import color
from skylines.lib.xcsoar_ import FlightPathFix
from skylines.model import User, TrackingFix
import xcsoar

track_blueprint = Blueprint('track', 'skylines')


@track_blueprint.url_value_preprocessor
def _pull_user_id(endpoint, values):
    g.user_id = values.pop('user_id')

    g.pilots = get_requested_record_list(
        User, g.user_id, joinedload=[User.club])

    color_gen = color.generator()
    for pilot in g.pilots:
        pilot.color = color_gen.next()


@track_blueprint.url_defaults
def _add_user_id(endpoint, values):
    if hasattr(g, 'user_id'):
        values.setdefault('user_id', g.user_id)


UNKNOWN_ELEVATION = -1000


def _get_flight_path2(pilot, last_update=None):
    query = TrackingFix.query() \
        .filter(and_(TrackingFix.pilot == pilot,
                     TrackingFix.location != None,
                     TrackingFix.altitude != None,
                     TrackingFix.max_age_filter(12)))

    if pilot.tracking_delay > 0 and not pilot.is_readable(g.current_user):
        query = query.filter(TrackingFix.delay_filter(pilot.tracking_delay))

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
                                    altitude=fix.altitude,
                                    enl=fix.engine_noise_level,
                                    track=fix.track,
                                    groundspeed=fix.ground_speed,
                                    tas=fix.airspeed,
                                    elevation=fix.elevation))

    return result


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

    encoded = dict(points=encoded_flight['locations'],
                   levels=encoded_flight['levels'],
                   zoom_levels=zoom_levels)

    barogram_t = encoded_flight['times']
    barogram_h = encoded_flight['altitude']
    enl = encoded_flight['enl']

    fp_reduced = map(lambda line: FlightPathFix(*line), xcsoar_flight.path())
    elevations = xcsoar.encode([fix.elevation if fix.elevation is not None else UNKNOWN_ELEVATION for fix in fp_reduced], method="signed")

    return dict(encoded=encoded, zoom_levels=zoom_levels, num_levels=num_levels,
                barogram_t=barogram_t, barogram_h=barogram_h, enl=enl,
                elevations=elevations)


@track_blueprint.route('/')
def index():
    traces = map(_get_flight_path, g.pilots)
    if not any(traces):
        traces = None

    return render_template(
        'tracking/view.jinja',
        pilots=g.pilots, traces=traces)


@track_blueprint.route('/map')
def map_():
    traces = map(_get_flight_path, g.pilots)
    if not any(traces):
        traces = None

    return render_template(
        'tracking/map.jinja',
        pilots=g.pilots, traces=traces)


@track_blueprint.route('/json')
def json():
    pilot = g.pilots[0]
    last_update = request.values.get('last_update', 0, type=int)

    trace = _get_flight_path(pilot, threshold=0.001, last_update=last_update)
    if not trace:
        abort(404)

    return jsonify(
        encoded=trace['encoded'],
        num_levels=trace['num_levels'],
        barogram_t=trace['barogram_t'],
        barogram_h=trace['barogram_h'],
        elevations=trace['elevations'],
        enl=trace['enl'],
        sfid=pilot.id)
