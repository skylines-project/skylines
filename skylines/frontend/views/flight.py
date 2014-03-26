import math
from datetime import datetime

from flask import Blueprint, request, render_template, redirect, url_for, abort, current_app, jsonify, g, flash
from flask.ext.babel import lazy_gettext as l_, _

from sqlalchemy.orm import undefer_group, contains_eager
from sqlalchemy.sql.expression import func
from geoalchemy2.shape import to_shape
from datetime import timedelta

from skylines.frontend.forms import ChangePilotsForm, ChangeAircraftForm
from skylines.lib import files
from skylines.lib.dbutil import get_requested_record_list
from skylines.lib.xcsoar_ import analyse_flight
from skylines.lib.helpers import format_time, format_number
from skylines.lib.formatter import units
from skylines.lib.datetime import from_seconds_of_day
from skylines.lib.geo import METERS_PER_DEGREE
from skylines.model import (
    db, User, Flight, FlightPhase, Location, FlightComment,
    Notification, Event
)
from skylines.model.event import create_flight_comment_notifications
from skylines.model.flight import get_elevations_for_flight
from skylines.worker import tasks
from redis.exceptions import ConnectionError

import xcsoar

flight_blueprint = Blueprint('flight', 'skylines')


def _reanalyse_if_needed(flight):
    if flight.needs_analysis:
        current_app.logger.info("Queueing flight %s for reanalysis" % flight.id)
        try:
            tasks.analyse_flight.delay(flight.id)
        except ConnectionError:
            current_app.logger.info('Cannot connect to Redis server')
            # analyse syncronously...
            analyse_flight(flight)
            db.session.commit()


@flight_blueprint.url_value_preprocessor
def _pull_flight_id(endpoint, values):
    g.flight_id = values.pop('flight_id')


def _patch_query(q):
    return q.join(Flight.igc_file) \
            .options(contains_eager(Flight.igc_file)) \
            .filter(Flight.is_viewable(g.current_user))


@flight_blueprint.before_request
def _query_flights():
    g.flights = get_requested_record_list(
        Flight, g.flight_id, patch_query=_patch_query)

    g.flight = g.flights[0]
    g.other_flights = g.flights[1:]

    if not g.flight.is_viewable(None):
        g.logout_next = url_for('index')

    map(_reanalyse_if_needed, g.flights)


@flight_blueprint.url_defaults
def _add_flight_id(endpoint, values):
    if hasattr(g, 'flight_id'):
        values.setdefault('flight_id', g.flight_id)


def _get_flight_path(flight, threshold=0.001, max_points=3000):
    num_levels = 4
    zoom_factor = 4
    zoom_levels = [0]
    zoom_levels.extend([round(-math.log(32.0 / 45.0 * (threshold * pow(zoom_factor, num_levels - i - 1)), 2)) for i in range(1, num_levels)])

    xcsoar_flight = xcsoar.Flight(files.filename_to_path(flight.igc_file.filename))

    begin = flight.takeoff_time - timedelta(seconds=2 * 60)
    end = flight.landing_time + timedelta(seconds=2 * 60)

    if begin > end:
        begin = datetime.min
        end = datetime.max

    xcsoar_flight.reduce(begin=begin,
                         end=end,
                         num_levels=num_levels,
                         zoom_factor=zoom_factor,
                         threshold=threshold,
                         max_points=max_points)

    encoded_flight = xcsoar_flight.encode()

    encoded = dict(points=encoded_flight['locations'],
                   levels=encoded_flight['levels'],
                   zoom_levels=zoom_levels)

    barogram_t = encoded_flight['times']
    barogram_h = encoded_flight['altitude']
    enl = encoded_flight['enl']

    elevations_t, elevations_h = _get_elevations(flight)
    contest_traces = _get_contest_traces(flight)

    return dict(encoded=encoded, zoom_levels=zoom_levels, num_levels=num_levels,
                barogram_t=barogram_t, barogram_h=barogram_h,
                enl=enl, contests=contest_traces,
                elevations_t=elevations_t, elevations_h=elevations_h,
                sfid=flight.id)


def _get_elevations(flight):
    elevations = get_elevations_for_flight(flight)

    # Encode lists
    elevations_t = xcsoar.encode([t for t, h in elevations], method="signed")
    elevations_h = xcsoar.encode([h for t, h in elevations], method="signed")

    return elevations_t, elevations_h


def _get_contest_traces(flight):
    contests = [dict(contest_type='olc_plus', trace_type='triangle'),
                dict(contest_type='olc_plus', trace_type='classic')]

    contest_traces = []

    for contest in contests:
        contest_trace = flight.get_optimised_contest_trace(contest['contest_type'], contest['trace_type'])
        if not contest_trace:
            continue

        fixes = map(lambda x: (x.latitude, x.longitude), contest_trace.locations)
        times = []
        for time in contest_trace.times:
            times.append(flight.takeoff_time.hour * 3600 + flight.takeoff_time.minute * 60 + flight.takeoff_time.second +
                         (time - flight.takeoff_time).days * 86400 + (time - flight.takeoff_time).seconds)

        contest_traces.append(dict(name=contest['contest_type'] + " " + contest['trace_type'],
                                   turnpoints=xcsoar.encode(fixes, floor=1e5, method="double"),
                                   times=xcsoar.encode(times, method="signed")))

    return contest_traces


CIRCDIR_NAMES = {None: "",
                 FlightPhase.CD_LEFT: l_("Left"),
                 FlightPhase.CD_MIXED: l_("Mixed"),
                 FlightPhase.CD_RIGHT: l_("Right"),
                 FlightPhase.CD_TOTAL: l_("Total")}

PHASETYPE_NAMES = {None: "",
                   FlightPhase.PT_POWERED: l_("Powered"),
                   FlightPhase.PT_CIRCLING: l_("Circling"),
                   FlightPhase.PT_CRUISE: l_("Cruise")}


def format_phase(phase):
    """Format phase properties to human readable format
    """
    is_circling = phase.phase_type == FlightPhase.PT_CIRCLING
    r = dict(start="%s" % format_time(phase.start_time),
             fraction="%d%%" % phase.fraction if phase.fraction is not None else "",
             speed=units.format_speed(phase.speed) if phase.speed is not None else "",
             vario=units.format_lift(phase.vario),
             alt_diff=units.format_altitude(phase.alt_diff),
             count=phase.count,
             duration=phase.duration,
             is_circling=is_circling,
             type=PHASETYPE_NAMES[phase.phase_type],
             circling_direction="",
             distance="",
             glide_rate="")

    if not is_circling:
        r['distance'] = units.format_distance(phase.distance, 1)

        # Sensible glide rate values are formatted as numbers. Others are shown
        # as infinity symbol.
        if abs(phase.alt_diff) > 0 and abs(phase.glide_rate) < 1000:
            r['glide_rate'] = format_number(phase.glide_rate)
        else:
            r['glide_rate'] = u'\u221e'  # infinity
    else:
        r['circling_direction'] = CIRCDIR_NAMES[phase.circling_direction]
    return r


def mark_flight_notifications_read(flight):
    if not g.current_user:
        return

    def add_flight_filter(query):
        return query.filter(Event.flight_id == flight.id)

    Notification.mark_all_read(g.current_user, filter_func=add_flight_filter)
    db.session.commit()


@flight_blueprint.route('/')
def index():
    def add_flight_path(flight):
        trace = _get_flight_path(flight)
        return (flight, trace)

    other_flights = map(add_flight_path, g.other_flights)

    mark_flight_notifications_read(g.flight)

    return render_template(
        'flights/view.jinja',
        flight=g.flight,
        trace=_get_flight_path(g.flight),
        other_flights=other_flights,
        phase_formatter=format_phase)


@flight_blueprint.route('/map')
def map_():
    def add_flight_path(flight):
        trace = _get_flight_path(flight, threshold=0.0001, max_points=10000)
        return (flight, trace)

    trace = _get_flight_path(g.flight, threshold=0.0001, max_points=10000)
    if trace is None:
        abort(404)

    other_flights = map(add_flight_path, g.other_flights)

    mark_flight_notifications_read(g.flight)

    return render_template(
        'flights/map.jinja',
        flight=g.flight, trace=trace, other_flights=other_flights)


@flight_blueprint.route('/json')
def json():
    trace = _get_flight_path(g.flight, threshold=0.0001, max_points=10000)
    if not trace:
        abort(404)

    return jsonify(
        encoded=trace['encoded'],
        num_levels=trace['num_levels'],
        zoom_levels=trace['zoom_levels'],
        barogram_t=trace['barogram_t'],
        barogram_h=trace['barogram_h'],
        enl=trace['enl'],
        contests=trace['contests'],
        elevations_t=trace['elevations_t'],
        elevations_h=trace['elevations_h'],
        sfid=g.flight.id,
        additional=dict(
            registration=g.flight.registration,
            competition_id=g.flight.competition_id))


def _get_near_flights(flight, location, time, max_distance=1000):
    # calculate max_distance in degrees at the earth's sphere (approximate,
    # cutoff at +-85 deg)
    max_distance_deg = (max_distance / METERS_PER_DEGREE) / \
        math.cos(math.radians(min(abs(location.latitude), 85)))

    # the distance filter is geometric only, so max_distance must be given in
    # SRID units (which is degrees for WGS84). The filter will be more and more
    # inaccurate further to the poles. But it's a lot faster than the geograpic
    # filter...

    result = Flight.query() \
        .options(undefer_group('path')) \
        .filter(Flight.id != flight.id) \
        .filter(Flight.takeoff_time <= time) \
        .filter(Flight.landing_time >= time) \
        .filter(func.ST_DWithin(Flight.locations,
                                location.to_wkt_element(),
                                max_distance_deg))

    result = _patch_query(result)

    flights = []
    for flight in result:
        # find point closest to given time
        closest = min(range(len(flight.timestamps)),
                      key=lambda x: abs((flight.timestamps[x] - time).total_seconds()))

        trace = to_shape(flight.locations).coords

        if closest == 0 or closest == len(trace) - 1:
            point = trace[closest]
        else:
            # interpolate flight trace between two fixes
            next_smaller = closest if flight.timestamps[closest] < time else closest - 1
            next_larger = closest if flight.timestamps[closest] > time else closest + 1
            dx = (time - flight.timestamps[next_smaller]).total_seconds() / \
                 (flight.timestamps[next_larger] - flight.timestamps[next_smaller]).total_seconds()

            point_next = trace[closest]
            point_prev = trace[closest]

            point = [point_prev[0] + (point_next[0] - point_prev[0]) * dx,
                     point_prev[1] + (point_next[1] - point_prev[1]) * dx]

        point_distance = location.geographic_distance(
            Location(latitude=point[1], longitude=point[0]))

        if point_distance > max_distance:
            continue

        flights.append(flight)

        # limit to 5 flights
        if len(flights) == 5:
            break

    return flights


@flight_blueprint.route('/near')
def near():
    try:
        latitude = float(request.args['lat'])
        longitude = float(request.args['lon'])
        time = float(request.args['time'])

    except (KeyError, ValueError):
        abort(400)

    location = Location(latitude=latitude, longitude=longitude)
    time = from_seconds_of_day(g.flight.takeoff_time, time)

    flights = _get_near_flights(g.flight, location, time, 1000)

    def add_flight_path(flight):
        trace = _get_flight_path(flight, threshold=0.0001, max_points=10000)
        trace['additional'] = dict(
            registration=flight.registration,
            competition_id=flight.competition_id)

        return trace

    return jsonify(flights=map(add_flight_path, flights))


@flight_blueprint.route('/change_pilot', methods=['GET', 'POST'])
def change_pilot():
    if not g.flight.is_writable(g.current_user):
        abort(403)

    form = ChangePilotsForm(obj=g.flight)
    if form.validate_on_submit():
        return change_pilot_post(form)

    return render_template('flights/change_pilot.jinja', form=form)


def change_pilot_post(form):
    pilot_id = form.pilot_id.data if form.pilot_id.data != 0 else None
    if g.flight.pilot_id != pilot_id:
        g.flight.pilot_id = pilot_id

        # update club if pilot changed
        if pilot_id:
            g.flight.club_id = User.get(pilot_id).club_id

    g.flight.pilot_name = form.pilot_name.data if form.pilot_name.data else None

    g.flight.co_pilot_id = form.co_pilot_id.data if form.co_pilot_id.data != 0 else None
    g.flight.co_pilot_name = form.co_pilot_name.data if form.co_pilot_name.data else None

    g.flight.time_modified = datetime.utcnow()
    db.session.commit()

    return redirect(url_for('.index'))


@flight_blueprint.route('/change_aircraft', methods=['GET', 'POST'])
def change_aircraft():
    if not g.flight.is_writable(g.current_user):
        abort(403)

    if g.flight.model_id is None:
        model_id = g.flight.igc_file.guess_model()
    else:
        model_id = g.flight.model_id

    if g.flight.registration is not None:
        registration = g.flight.registration
    elif g.flight.igc_file.registration is not None:
        registration = g.flight.igc_file.registration
    else:
        registration = g.flight.igc_file.guess_registration()

    if g.flight.competition_id is not None:
        competition_id = g.flight.competition_id
    elif g.flight.igc_file.competition_id is not None:
        competition_id = g.flight.igc_file.competition_id
    else:
        competition_id = None

    form = ChangeAircraftForm(
        model_id=model_id,
        registration=registration,
        competition_id=competition_id
    )
    if form.validate_on_submit():
        return change_aircraft_post(form)

    return render_template('flights/change_aircraft.jinja', form=form)


def change_aircraft_post(form):
    registration = form.registration.data
    if registration is not None:
        registration = registration.strip()
        if len(registration) == 0:
            registration = None

    g.flight.model_id = form.model_id.data or None
    g.flight.registration = registration
    g.flight.competition_id = form.competition_id.data or None
    g.flight.time_modified = datetime.utcnow()
    db.session.commit()

    return redirect(url_for('.index'))


@flight_blueprint.route('/delete', methods=['GET', 'POST'])
def delete():
    if not g.flight.is_writable(g.current_user):
        abort(403)

    if request.method == 'POST':
        files.delete_file(g.flight.igc_file.filename)
        db.session.delete(g.flight)
        db.session.delete(g.flight.igc_file)
        db.session.commit()

        return redirect(url_for('flights.index'))

    return render_template(
        'generic/confirm.jinja',
        title=_('Delete Flight'),
        question=_('Are you sure you want to delete this flight?'),
        action=url_for('.delete'), cancel=url_for('.index'))


@flight_blueprint.route('/add_comment', methods=['POST'])
def add_comment():
    if not g.current_user:
        flash(_('You have to be logged in to post comments!'), 'warning')
        return redirect(url_for('.index'))

    text = request.form['text'].strip()
    if not text:
        return redirect(url_for('.index'))

    comment = FlightComment()
    comment.user = g.current_user
    comment.flight = g.flight
    comment.text = text

    create_flight_comment_notifications(comment)

    db.session.commit()

    return redirect(url_for('.index'))


@flight_blueprint.route('/analysis')
def analysis():
    """Hidden method that restarts flight analysis."""

    if not g.current_user or not g.current_user.is_manager():
        abort(403)

    analyse_flight(g.flight)
    db.session.commit()

    return redirect(url_for('.index'))
