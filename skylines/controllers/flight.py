import math
import logging
from datetime import datetime
from tg import expose, validate, require, request, redirect, flash
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.decorators import with_trailing_slash, without_trailing_slash
from repoze.what.predicates import has_permission
from webob.exc import HTTPBadRequest, HTTPNotFound, HTTPForbidden
from formencode.validators import String
from tw.forms.fields import TextField
from sprox.formbase import EditableForm
from sprox.widgets import PropertySingleSelectField
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement
from sqlalchemy.sql.expression import func
from skylines.controllers.base import BaseController
from skylines.lib import files
from sqlalchemy.sql.expression import and_, literal_column
from skylines.model import (DBSession, User, Flight, FlightPhase, Location,
                            Elevation)
from skylines.model.flight_comment import FlightComment
from skylines.model.notification import create_flight_comment_notifications
from skylines.lib.xcsoar import analyse_flight, flight_path
from skylines.lib.helpers import format_time, format_number
from skylines.lib.formatter import units
from skylines.lib.datetime import from_seconds_of_day
from skylines.lib.geo import METERS_PER_DEGREE
from skylines.forms import BootstrapForm, aircraft_model
from skylines.lib.sql import extract_array_item
from skylinespolyencode import SkyLinesPolyEncoder

log = logging.getLogger(__name__)


class PilotSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        query = DBSession.query(User.id, User.display_name) \
            .filter(User.club_id == request.identity['user'].club_id) \
            .order_by(User.display_name)
        options = [(None, 'None')] + query.all()
        d['options'] = options
        return d

    def validate(self, value, *args, **kw):
        if isinstance(value, User):
            value = value.id
        return super(PilotSelectField, self).validate(value, *args, **kw)


class SelectPilotForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Flight
    __hide_fields__ = ['id']
    __limit_fields__ = ['pilot', 'co_pilot']
    __base_widget_args__ = dict(action='select_pilot')
    pilot = PilotSelectField('pilot', label_text=l_('Pilot'))
    co_pilot = PilotSelectField('co_pilot', label_text=l_('Co-Pilot'))

select_pilot_form = SelectPilotForm(DBSession)


class SelectAircraftForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Flight
    __hide_fields__ = ['id']
    __limit_fields__ = ['model', 'registration', 'competition_id']
    __base_widget_args__ = dict(action='select_aircraft')
    model = aircraft_model.SelectField('model', label_text=l_('Aircraft Model'))
    registration = TextField('registration', label_text=l_('Aircraft Registration'), maxlength=32, validator=String(max=32))
    competition_id = TextField('competition_id', label_text=l_('Competition Number'), maxlength=5, validator=String(max=5))

select_aircraft_form = SelectAircraftForm(DBSession)


def get_flight_path(flight, threshold=0.001, max_points=3000):
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

    elevations_t, elevations_h = get_elevations(flight, encoder)
    contest_traces = get_contest_traces(flight, encoder)

    return dict(encoded=encoded, zoom_levels=zoom_levels, num_levels=num_levels,
                barogram_t=barogram_t, barogram_h=barogram_h,
                enl=enl, contests=contest_traces,
                elevations_t=elevations_t, elevations_h=elevations_h,
                sfid=flight.id)


def get_elevations(flight, encoder):
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


def get_contest_traces(flight, encoder):
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


def get_near_flights(flight, location, time, max_distance=1000):
    # calculate max_distance in degrees at the earth's sphere (approximate,
    # cutoff at +-85 deg)
    max_distance_deg = (max_distance / METERS_PER_DEGREE) / \
        math.cos(math.radians(min(abs(location.latitude), 85)))

    # the distance filter is geometric only, so max_distance must be given in
    # SRID units (which is degrees for WGS84). The filter will be more and more
    # inaccurate further to the poles. But it's a lot faster than the geograpic
    # filter...

    result = DBSession.query(Flight) \
        .filter(Flight.id != flight.id) \
        .filter(Flight.takeoff_time <= time) \
        .filter(Flight.landing_time >= time) \
        .filter(func.ST_DWithin(Flight.locations,
                                WKTElement(location.to_wkt()),
                                max_distance_deg))

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


class FlightController(BaseController):
    def __init__(self, flight):
        if isinstance(flight, list):
            map(self.__reanalyse_if_needed, flight)
            self.flight = flight[0]
            self.other_flights = flight[1:]
        else:
            self.__reanalyse_if_needed(flight)
            self.flight = flight
            self.other_flights = None

    def __reanalyse_if_needed(self, flight):
        if flight.needs_analysis:
            log.info("Reanalysing flight %s" % flight.id)
            analyse_flight(flight)

    def __get_flight_path(self, **kw):
        return get_flight_path(self.flight, **kw)

    @with_trailing_slash
    @expose('flights/view.jinja')
    def index(self, **kwargs):
        def add_flight_path(flight):
            trace = get_flight_path(flight)
            return (flight, trace)

        other_flights = map(add_flight_path, self.other_flights)
        return dict(flight=self.flight,
                    trace=self.__get_flight_path(),
                    other_flights=other_flights,
                    phase_formatter=format_phase)

    @without_trailing_slash
    @expose('flights/map.jinja')
    def map(self, **kwargs):
        def add_flight_path(flight):
            trace = get_flight_path(flight, threshold=0.0001, max_points=10000)
            return (flight, trace)

        trace = self.__get_flight_path(threshold=0.0001, max_points=10000)
        if trace is None:
            raise HTTPNotFound

        other_flights = map(add_flight_path, self.other_flights)

        return dict(flight=self.flight, trace=trace,
                    other_flights=other_flights)

    @expose('json')
    def json(self, **kwargs):
        trace = self.__get_flight_path(threshold=0.0001, max_points=10000)

        if not trace:
            raise HTTPNotFound

        return dict(encoded=trace['encoded'],
                    num_levels=trace['num_levels'],
                    zoom_levels=trace['zoom_levels'],
                    barogram_t=trace['barogram_t'],
                    barogram_h=trace['barogram_h'],
                    enl=trace['enl'],
                    contests=trace['contests'],
                    elevations_t=trace['elevations_t'],
                    elevations_h=trace['elevations_h'],
                    sfid=self.flight.id,
                    additional=dict(
                        registration=self.flight.registration,
                        competition_id=self.flight.competition_id))

    @expose('json')
    def near(self, **kwargs):
        try:
            latitude = float(kwargs['lat'])
            longitude = float(kwargs['lon'])
            time = float(kwargs['time'])

        except (KeyError, ValueError):
            raise HTTPBadRequest

        location = Location(latitude=latitude,
                            longitude=longitude)
        time = from_seconds_of_day(self.flight.takeoff_time, time)

        flights = get_near_flights(self.flight, location, time, 1000)

        def add_flight_path(flight):
            trace = get_flight_path(flight, threshold=0.0001, max_points=10000)
            trace['additional'] = dict(
                registration=flight.registration,
                competition_id=flight.competition_id)

            return trace

        return dict(flights=map(add_flight_path, flights))

    @without_trailing_slash
    @expose('generic/form.jinja')
    def change_pilot(self, **kwargs):
        if not self.flight.is_writable(request.identity):
            raise HTTPForbidden

        return dict(active_page='flights', title=_('Select Pilot'),
                    user=request.identity['user'],
                    include_after='flights/after_change_pilot.jinja',
                    form=select_pilot_form,
                    values=self.flight)

    @without_trailing_slash
    @expose()
    @validate(form=select_pilot_form, error_handler=change_pilot)
    def select_pilot(self, pilot, co_pilot, **kwargs):
        if not self.flight.is_writable(request.identity):
            raise HTTPForbidden

        if self.flight.pilot_id != pilot:
            self.flight.pilot_id = pilot
            if pilot:
                self.flight.club_id = DBSession.query(User).get(pilot).club_id
        self.flight.co_pilot_id = co_pilot
        self.flight.time_modified = datetime.utcnow()
        DBSession.flush()

        redirect('.')

    @without_trailing_slash
    @expose('generic/form.jinja')
    def change_aircraft(self, **kwargs):
        if not self.flight.is_writable(request.identity):
            raise HTTPForbidden

        if self.flight.model_id is None:
            model_id = self.flight.igc_file.guess_model()
        else:
            model_id = self.flight.model_id

        if self.flight.registration is not None:
            registration = self.flight.registration
        elif self.flight.igc_file.registration is not None:
            registration = self.flight.igc_file.registration
        else:
            registration = self.flight.igc_file.guess_registration()

        if self.flight.competition_id is not None:
            competition_id = self.flight.competition_id
        elif self.flight.igc_file.competition_id is not None:
            competition_id = self.flight.igc_file.competition_id
        else:
            competition_id = None

        return dict(active_page='flights', title=_('Change Aircraft'),
                    form=select_aircraft_form,
                    values=dict(id=self.flight.id,
                                model=model_id,
                                registration=registration,
                                competition_id=competition_id))

    @without_trailing_slash
    @expose()
    @validate(form=select_aircraft_form, error_handler=change_aircraft)
    def select_aircraft(self, model, registration, competition_id, **kwargs):
        if not self.flight.is_writable(request.identity):
            raise HTTPForbidden

        if registration is not None:
            registration = registration.strip()
            if len(registration) == 0:
                registration = None

        self.flight.model_id = model
        self.flight.registration = registration
        self.flight.competition_id = competition_id
        self.flight.time_modified = datetime.utcnow()
        DBSession.flush()

        redirect('.')

    @without_trailing_slash
    @expose()
    @require(has_permission('upload'))
    def analysis(self, **kwargs):
        """Hidden method that restarts flight analysis."""

        analyse_flight(self.flight)
        DBSession.flush()

        return redirect('.')

    @without_trailing_slash
    @expose('generic/confirm.jinja')
    def delete(self, **kwargs):
        if not self.flight.is_writable(request.identity):
            raise HTTPForbidden

        if request.method == 'POST':
            files.delete_file(self.flight.igc_file.filename)
            DBSession.delete(self.flight)
            DBSession.delete(self.flight.igc_file)

            redirect('/flights/')
        else:
            return dict(title=_('Delete Flight'),
                        question=_('Are you sure you want to delete this flight?'),
                        action='delete', cancel='.')

    @without_trailing_slash
    @expose()
    def add_comment(self, text, **kwargs):
        if request.identity is None:
            flash(_('You have to be logged in to post comments!'), 'warning')
        else:
            text = text.strip()
            if len(text) == 0:
                redirect('.')

            comment = FlightComment()
            comment.user = request.identity['user']
            comment.flight = self.flight
            comment.text = text

            create_flight_comment_notifications(comment)

        redirect('.')
