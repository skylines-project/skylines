import math
from datetime import datetime

from flask import Blueprint, request, render_template, redirect, url_for, abort, current_app, jsonify, g
from flask.ext.babel import lazy_gettext as l_

from formencode.validators import String
from tw.forms.fields import TextField
from sprox.formbase import EditableForm
from sprox.widgets import PropertySingleSelectField

from sqlalchemy.sql.expression import func, and_, literal_column
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement

from skylines.forms import BootstrapForm, aircraft_model
from skylines.lib import files
from skylines.lib.dbutil import get_requested_record_list
from skylines.lib.xcsoar import analyse_flight, flight_path
from skylines.lib.helpers import format_time, format_number
from skylines.lib.formatter import units
from skylines.lib.datetime import from_seconds_of_day
from skylines.lib.geo import METERS_PER_DEGREE
from skylines.lib.sql import extract_array_item
from skylines.model import (
    DBSession, User, Flight, FlightPhase, Location, Elevation, FlightComment
)
from skylines.model.notification import create_flight_comment_notifications
from skylinespolyencode import SkyLinesPolyEncoder

flight_blueprint = Blueprint('flight', 'skylines')


def _reanalyse_if_needed(flight):
    if flight.needs_analysis:
        current_app.logger.info("Reanalysing flight %s" % flight.id)
        analyse_flight(flight)


@flight_blueprint.url_value_preprocessor
def _pull_flight_id(endpoint, values):
    flight_ids = values.pop('flight_id')
    g.flights = get_requested_record_list(Flight, flight_ids)
    g.flight = g.flights[0]
    g.other_flights = g.flights[1:]

    map(_reanalyse_if_needed, g.flights)


def _get_flight_path(flight, threshold=0.001, max_points=3000):
    fp = flight_path(flight.igc_file, max_points)
    if len(fp) == 0:
        log.error('flight_path("' + flight.igc_file.filename + '") returned with an empty list')
        return None

    num_levels = 4
    zoom_factor = 4
    zoom_levels = [0]
    zoom_levels.extend([round(-math.log(32.0 / 45.0 * (threshold * pow(zoom_factor, num_levels - i - 1)), 2)) for i in range(1, num_levels)])

    max_delta_time = max(4, (fp[-1].seconds_of_day - fp[0].seconds_of_day) / 500)

    encoder = SkyLinesPolyEncoder(num_levels=4, threshold=threshold, zoom_factor=4)

    fixes = map(lambda x: (x.longitude, x.latitude,
                           (x.seconds_of_day / max_delta_time * threshold)), fp)
    fixes = encoder.classify(fixes, remove=False, type="ppd")

    encoded = encoder.encode(fixes['points'], fixes['levels'])

    barogram_t = encoder.encodeList([fp[i].seconds_of_day for i in range(len(fp)) if fixes['levels'][i] != -1])
    barogram_h = encoder.encodeList([fp[i].altitude for i in range(len(fp)) if fixes['levels'][i] != -1])
    enl = encoder.encodeList([fp[i].enl for i in range(len(fp)) if fixes['levels'][i] != -1])

    elevations_t, elevations_h = _get_elevations(flight, encoder)
    contest_traces = _get_contest_traces(flight, encoder)

    return dict(encoded=encoded, zoom_levels=zoom_levels, num_levels=num_levels,
                barogram_t=barogram_t, barogram_h=barogram_h,
                enl=enl, contests=contest_traces,
                elevations_t=elevations_t, elevations_h=elevations_h,
                sfid=flight.id)


def _get_elevations(flight, encoder):
    # Prepare column expressions
    locations = Flight.locations.ST_DumpPoints()
    location_id = extract_array_item(locations.path, 1)
    location = locations.geom

    # Prepare subquery
    subq = DBSession.query(location_id.label('location_id'),
                           location.label('location')) \
                    .filter(Flight.id == flight.id).subquery()

    # Prepare column expressions
    timestamp = literal_column('timestamps[location_id]')
    elevation = Elevation.rast.ST_Value(subq.c.location)

    # Prepare main query
    q = DBSession.query(timestamp.label('timestamp'),
                        elevation.label('elevation')) \
                 .filter(and_(Flight.id == flight.id,
                              subq.c.location.ST_Intersects(Elevation.rast),
                              elevation != None)).all()

    if len(q) == 0:
        return [], []

    # Assemble elevation data
    elevations_t = []
    elevations_h = []

    start_time = q[0][0]
    start_midnight = start_time.replace(hour=0, minute=0, second=0, microsecond=0)

    for time, elevation in q:
        time_delta = time - start_midnight
        time = time_delta.days * 86400 + time_delta.seconds

        elevations_t.append(time)
        elevations_h.append(elevation)

    # Encode lists
    elevations_t = encoder.encodeList(elevations_t)
    elevations_h = encoder.encodeList(elevations_h)

    return elevations_t, elevations_h


def _get_contest_traces(flight, encoder):
    contests = [dict(contest_type='olc_plus', trace_type='triangle'),
                dict(contest_type='olc_plus', trace_type='classic')]

    contest_traces = []

    for contest in contests:
        contest_trace = flight.get_optimised_contest_trace(contest['contest_type'], contest['trace_type'])
        if not contest_trace:
            continue

        fixes = map(lambda x: (x.longitude, x.latitude), contest_trace.locations)
        times = []
        for time in contest_trace.times:
            times.append(flight.takeoff_time.hour * 3600 + flight.takeoff_time.minute * 60 + flight.takeoff_time.second +
                         (time - flight.takeoff_time).days * 86400 + (time - flight.takeoff_time).seconds)

        contest_traces.append(dict(name=contest['contest_type'] + " " + contest['trace_type'],
                                   turnpoints=encoder.encode(fixes, [0] * len(fixes))['points'],
                                   times=encoder.encodeList(times)))

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
        r['distance'] = units.format_distance(phase.distance)

        # Sensible glide rate values are formatted as numbers. Others are shown
        # as infinity symbol.
        if abs(phase.alt_diff) > 0 and abs(phase.glide_rate) < 1000:
            r['glide_rate'] = format_number(phase.glide_rate)
        else:
            r['glide_rate'] = u'\u221e'  # infinity
    else:
        r['circling_direction'] = CIRCDIR_NAMES[phase.circling_direction]
    return r


@flight_blueprint.route('/')
def index():
    def add_flight_path(flight):
        trace = _get_flight_path(flight)
        return (flight, trace)

    other_flights = map(add_flight_path, g.other_flights)

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
