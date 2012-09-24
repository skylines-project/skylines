# -*- coding: utf-8 -*-

import math
import logging
from babel.dates import format_date
from datetime import datetime, timedelta
from tg import expose, validate, require, request, redirect, config, flash
from tg.i18n import ugettext as _
from tg.decorators import with_trailing_slash, without_trailing_slash
from repoze.what.predicates import has_permission
from webob.exc import HTTPNotFound, HTTPForbidden
from sqlalchemy.sql.expression import desc, or_, and_, between
from sqlalchemy import func
from sqlalchemy.orm import joinedload, subqueryload, contains_eager
from sqlalchemy.orm.util import aliased
from tw.forms.fields import TextField
from sprox.formbase import EditableForm
from sprox.widgets import PropertySingleSelectField
from skylines.lib.base import BaseController
from skylines import files
from skylines.model import (DBSession, User, Club, Flight, IGCFile, Model,
                            Airport, FlightPhase)
from skylines.model.flight_comment import FlightComment
from skylines.model.notification import create_flight_comment_notifications
from skylines.controllers.upload import UploadController
from skylines.lib.datatables import GetDatatableRecords
from skylines.lib.analysis import analyse_flight, flight_path
from skylines.lib.helpers import truncate, format_time, format_number
from skylines.lib.dbutil import get_requested_record, get_requested_record_list
from skylines.lib import units
from skylines.form import BootstrapForm
from skylinespolyencode import SkyLinesPolyEncoder

log = logging.getLogger(__name__)


class PilotSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        query = DBSession.query(User.user_id, User.display_name) \
                .filter(User.club_id == request.identity['user'].club_id) \
                .order_by(User.display_name)
        options = [(None, 'None')] + query.all()
        d['options'] = options
        return d

    def validate(self, value, *args, **kw):
        if isinstance(value, User):
            value = value.user_id
        return super(PilotSelectField, self).validate(value, *args, **kw)


class SelectPilotForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Flight
    __hide_fields__ = ['id']
    __limit_fields__ = ['pilot', 'co_pilot']
    __base_widget_args__ = dict(action='select_pilot')
    pilot = PilotSelectField
    co_pilot = PilotSelectField

select_pilot_form = SelectPilotForm(DBSession)


class ModelSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        query = DBSession.query(Model.id, Model.name) \
                .order_by(Model.name)
        options = [(None, '[unspecified]')] + query.all()
        d['options'] = options
        return d


class SelectAircraftForm(EditableForm):
    __base_widget_type__ = BootstrapForm
    __model__ = Flight
    __hide_fields__ = ['id']
    __limit_fields__ = ['model', 'registration']
    __base_widget_args__ = dict(action='select_aircraft')
    model = ModelSelectField
    registration = TextField

select_aircraft_form = SelectAircraftForm(DBSession)


def get_flight_path(flight, threshold = 0.001, max_points = 3000):
    fp = flight_path(flight.igc_file, max_points)
    if len(fp) == 0:
        log.error('flight_path("' + flight.igc_file.filename + '") returned with an empty list')
        return None

    num_levels = 4
    zoom_factor = 4
    zoom_levels = [0]
    zoom_levels.extend([round(-math.log(32.0 / 45.0 * (threshold * pow(zoom_factor, num_levels - i - 1)), 2)) for i in range(1, num_levels)])

    max_delta_time = max(4, (fp[-1][0] - fp[0][0]) / 500)

    encoder = SkyLinesPolyEncoder(num_levels=4, threshold=threshold, zoom_factor=4)

    fixes = map(lambda x: (x[2], x[1], (x[0] / max_delta_time * threshold)), fp)
    fixes = encoder.classify(fixes, remove=False, type="ppd")

    encoded = encoder.encode(fixes['points'], fixes['levels'])

    barogram_t = encoder.encodeList([fp[i][0] for i in range(len(fp)) if fixes['levels'][i] != -1])
    barogram_h = encoder.encodeList([fp[i][3] for i in range(len(fp)) if fixes['levels'][i] != -1])
    enl = encoder.encodeList([fp[i][4] for i in range(len(fp)) if fixes['levels'][i] != -1])

    contest_traces = get_contest_traces(flight, encoder)

    return dict(encoded=encoded, zoom_levels = zoom_levels, fixes = fixes,
                barogram_t=barogram_t, barogram_h=barogram_h, enl=enl, contests = contest_traces,
                sfid=flight.id)


def get_contest_traces(flight, encoder):
    contests = [dict(contest_type = 'olc_plus', trace_type = 'triangle'),
                dict(contest_type = 'olc_plus', trace_type = 'classic')]

    contest_traces = []

    for contest in contests:
        contest_trace = flight.get_optimised_contest_trace(contest['contest_type'], contest['trace_type'])
        if not contest_trace:
            continue

        fixes = map(lambda x: (x.longitude, x.latitude), contest_trace.locations)
        times = []
        for time in contest_trace.times:
            times.append(flight.takeoff_time.hour * 3600 + flight.takeoff_time.minute * 60 + flight.takeoff_time.second + \
                         (time - flight.takeoff_time).days * 86400 + (time - flight.takeoff_time).seconds)

        contest_traces.append(dict(name = contest['contest_type'] + " " + contest['trace_type'],
                                   turnpoints = encoder.encode(fixes, [0] * len(fixes))['points'],
                                   times = encoder.encodeList(times)))

    return contest_traces

CIRCDIR_NAMES = {None: "",
                 FlightPhase.CD_LEFT: "Left",
                 FlightPhase.CD_MIXED: "Mixed",
                 FlightPhase.CD_RIGHT: "Right",
                 FlightPhase.CD_TOTAL: "Total"}

PHASETYPE_NAMES = {None: "",
                   FlightPhase.PT_POWERED: "Powered",
                   FlightPhase.PT_CIRCLING: "Circling",
                   FlightPhase.PT_CRUISE: "Cruise"}


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
            r['glide_rate'] = u'\u221e' # infinity
    else:
        r['circling_direction'] = CIRCDIR_NAMES[phase.circling_direction]
    return r


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
    @expose('skylines.templates.flights.view')
    def index(self):
        def add_flight_path(flight):
            trace = get_flight_path(flight)
            return (flight, trace)

        other_flights = map(add_flight_path, self.other_flights)
        return dict(flight=self.flight,
                    trace=self.__get_flight_path(),
                    other_flights=other_flights,
                    phase_formatter=format_phase)

    @without_trailing_slash
    @expose('skylines.templates.flights.map')
    def map(self):
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
    def json(self):
        trace = self.__get_flight_path(threshold=0.0001, max_points=10000)

        if not trace:
            raise HTTPNotFound

        return  dict(encoded=trace['encoded'], num_levels=trace['fixes']['numLevels'],
                     zoom_levels=trace['zoom_levels'], barogram_t=trace['barogram_t'],
                     barogram_h=trace['barogram_h'], enl=trace['enl'], contests=trace['contests'],
                     sfid=self.flight.id)

    @without_trailing_slash
    @expose('skylines.templates.generic.form')
    def change_pilot(self):
        if not self.flight.is_writable():
            raise HTTPForbidden

        return dict(page='settings', title=_('Select Pilot'),
                    user=request.identity['user'],
                    include_after='flights/after_change_pilot.html',
                    form=select_pilot_form,
                    values=self.flight)

    @without_trailing_slash
    @expose()
    @validate(form=select_pilot_form, error_handler=change_pilot)
    def select_pilot(self, pilot, co_pilot, **kwargs):
        if not self.flight.is_writable():
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
    @expose('skylines.templates.generic.form')
    def change_aircraft(self):
        if not self.flight.is_writable():
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

        return dict(page='settings', title=_('Change Aircraft'),
                    user=request.identity['user'],
                    form=select_aircraft_form,
                    values=dict(model=model_id,
                                registration=registration))

    @without_trailing_slash
    @expose()
    @validate(form=select_aircraft_form, error_handler=change_aircraft)
    def select_aircraft(self, model, registration, **kwargs):
        if not self.flight.is_writable():
            raise HTTPForbidden

        if registration is not None:
            registration = registration.strip()
            if len(registration) == 0:
                registration = None

        self.flight.model_id = model
        self.flight.registration = registration
        self.flight.time_modified = datetime.utcnow()
        DBSession.flush()

        redirect('.')

    @without_trailing_slash
    @expose()
    @require(has_permission('upload'))
    def analysis(self):
        """Hidden method that restarts flight analysis."""

        analyse_flight(self.flight)
        DBSession.flush()

        return redirect('.')

    @without_trailing_slash
    @expose('skylines.templates.generic.confirm')
    def delete(self, yes=False):
        if not self.flight.is_writable():
            raise HTTPForbidden

        if yes:
            files.delete_file(self.flight.igc_file.filename)
            DBSession.delete(self.flight)
            DBSession.delete(self.flight.igc_file)

            redirect('/flights/')
        else:
            return dict(title='Delete Flight',
                        question='Are you sure you want to delete this flight?',
                        action='', cancel='.')

    @without_trailing_slash
    @expose()
    def add_comment(self, text):
        if request.identity is None:
            flash(_('You have to be logged in to post comments!'), 'warning')
        else:
            comment = FlightComment()
            comment.user = request.identity['user']
            comment.flight = self.flight
            comment.text = text

            create_flight_comment_notifications(comment)

        redirect('.')


class FlightsController(BaseController):
    def __do_list(self, tab, kw, date=None, pilot=None, club=None, airport=None, \
                  pinned=None, filter=None, columns=None):
        pilot_alias = aliased(User, name='pilot')
        owner_alias = aliased(User, name='owner')

        subq = DBSession.query(FlightComment.flight_id,
                               func.count('*').label('count')) \
               .group_by(FlightComment.flight_id).subquery()

        flights = DBSession.query(Flight, subq.c.count) \
            .outerjoin(Flight.igc_file) \
            .options(contains_eager(Flight.igc_file)) \
            .outerjoin(owner_alias, IGCFile.owner) \
            .options(contains_eager(Flight.igc_file, IGCFile.owner, alias=owner_alias)) \
            .outerjoin(pilot_alias, Flight.pilot) \
            .options(contains_eager(Flight.pilot, alias=pilot_alias)) \
            .options(joinedload(Flight.co_pilot)) \
            .outerjoin(Flight.club) \
            .options(contains_eager(Flight.club)) \
            .outerjoin(Flight.takeoff_airport) \
            .options(contains_eager(Flight.takeoff_airport)) \
            .outerjoin(Flight.model) \
            .options(contains_eager(Flight.model)) \
            .outerjoin((subq, Flight.comments))

        if date:
            flights = flights.filter(Flight.date_local == date)

        if pilot:
            flights = flights.filter(or_(Flight.pilot == pilot,
                                         Flight.co_pilot == pilot))
        if club:
            flights = flights.filter(Flight.club == club)

        if airport:
            flights = flights.filter(Flight.takeoff_airport == airport)

        if pinned:
            flights = flights.filter(Flight.id.in_(pinned))

        if filter is not None:
            flights = flights.filter(filter)

        if request.response_type == 'application/json':
            if not columns:
                columns = {
                    0: 'date_local',
                    1: 'olc_plus_score',
                    2: 'pilot.display_name',
                    3: 'olc_classic_distance',
                    4: 'airports.name',
                    5: 'clubs.name',
                    6: 'models.name',
                    7: 'takeoff_time',
                    8: 'id',
                    9: 'num_comments',
                }

            flights, response_dict = GetDatatableRecords(kw, flights, columns)

            aaData = []
            for flight, num_comments in flights:
                aaData.append(dict(takeoff_time = flight.takeoff_time.strftime('%H:%M'),
                                   landing_time = flight.landing_time.strftime('%H:%M'),
                                   date = flight.date_local.strftime('%d.%m.%Y'),
                                   date_formatted = format_date(flight.date_local),
                                   olc_plus_score = flight.olc_plus_score,
                                   olc_classic_distance = flight.olc_classic_distance,
                                   pilot_id = flight.pilot_id,
                                   pilot = flight.pilot and flight.pilot.display_name,
                                   co_pilot_id = flight.co_pilot_id,
                                   co_pilot = flight.co_pilot and flight.co_pilot.display_name,
                                   club_id = flight.club_id,
                                   club = flight.club and truncate(flight.club.name, 25),
                                   owner = flight.igc_file.owner.display_name,
                                   takeoff_airport = flight.takeoff_airport and flight.takeoff_airport.name,
                                   takeoff_airport_id = flight.takeoff_airport and flight.takeoff_airport.id,
                                   takeoff_airport_country_code = flight.takeoff_airport and flight.takeoff_airport.country_code.lower(),
                                   aircraft = (flight.model and flight.model.name) or (flight.igc_file.model and '[' + flight.igc_file.model + ']'),
                                   aircraft_reg = flight.registration or flight.igc_file.registration or "Unknown",
                                   flight_id = flight.id,
                                   num_comments = num_comments))

            return dict(response_dict, aaData = aaData)

        else:
            if not date:
                flights = flights.order_by(desc(Flight.date_local))

            flights_count = flights.count()
            if flights_count > int(config.get('skylines.lists.server_side', 250)):
                limit = int(config.get('skylines.lists.display_length', 50))
            else:
                limit = int(config.get('skylines.lists.server_side', 250))

            flights = flights.order_by(desc(Flight.olc_plus_score))
            flights = flights.limit(limit)
            return dict(tab = tab, date=date, pilot=pilot, club=club, airport=airport,
                        flights = flights, flights_count = flights_count)

    @expose()
    def lookup(self, id, *remainder):
        # Fallback for old URLs
        if id == 'id' and len(remainder) > 0:
            id = remainder[0]
            remainder = remainder[1:]

        flights = get_requested_record_list(Flight, id,
                                            joinedload=[Flight.igc_file])
        controller = FlightController(flights)
        return controller, remainder

    @with_trailing_slash
    @expose()
    def index(self, **kw):
        redirect('today')

    @without_trailing_slash
    @expose('skylines.templates.flights.list')
    @expose('json')
    def all(self, **kw):
        return self.__do_list('all', kw)

    @without_trailing_slash
    @expose('skylines.templates.flights.list')
    @expose('json')
    def today(self, **kw):
        query = DBSession.query(func.max(Flight.date_local).label('date')) \
                         .filter(Flight.takeoff_time < datetime.utcnow())

        date = query.one().date
        if not date:
            raise HTTPNotFound

        return self.date(date, today = True, **kw)

    @without_trailing_slash
    @expose('skylines.templates.flights.list')
    @expose('json')
    def date(self, date, **kw):
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, "%Y-%m-%d")

            if isinstance(date, datetime):
                date = date.date()
        except:
            raise HTTPNotFound

        columns = {
            0: 'olc_plus_score',
            1: 'pilot.display_name',
            2: 'olc_classic_distance',
            3: 'airports.name',
            4: 'clubs.name',
            5: 'models.name',
            6: 'takeoff_time',
            7: 'id',
            8: 'num_comments',
        }

        if kw.get('today', False):
            return self.__do_list('today', kw, date=date, columns=columns)
        else:
            return self.__do_list('date', kw, date=date, columns=columns)

    @without_trailing_slash
    @expose()
    def my(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        redirect('pilot/' + str(request.identity['user'].user_id))

    @without_trailing_slash
    @expose()
    def my_club(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        redirect('club/' + str(request.identity['user'].club.id))

    @without_trailing_slash
    @expose('skylines.templates.flights.list')
    @expose('json')
    def unassigned(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        f = and_(Flight.pilot_id == None,
                 IGCFile.owner == request.identity['user'])
        return self.__do_list('unassigned', kw, filter=f)

    @expose('skylines.templates.flights.list')
    @expose('json')
    def pilot(self, id, **kw):
        pilot = get_requested_record(User, id)

        columns = {
            0: 'date_local',
            1: 'olc_plus_score',
            2: 'pilot.display_name',
            3: 'olc_classic_distance',
            4: 'airports.name',
            5: 'models.name',
            6: 'takeoff_time',
            7: 'id',
            8: 'num_comments',
        }

        return self.__do_list('pilot', kw, pilot=pilot, columns=columns)

    @expose('skylines.templates.flights.list')
    @expose('json')
    def club(self, id, **kw):
        club = get_requested_record(Club, id)

        columns = {
            0: 'date_local',
            1: 'olc_plus_score',
            2: 'pilot.display_name',
            3: 'olc_classic_distance',
            4: 'airports.name',
            5: 'models.name',
            6: 'takeoff_time',
            7: 'id',
            8: 'num_comments',
        }

        return self.__do_list('club', kw, club=club, columns=columns)

    @expose('skylines.templates.flights.list')
    @expose('json')
    def airport(self, id, **kw):
        airport = get_requested_record(Airport, id)

        columns = {
            0: 'date_local',
            1: 'olc_plus_score',
            2: 'pilot.display_name',
            3: 'olc_classic_distance',
            4: 'clubs.name',
            5: 'models.name',
            6: 'takeoff_time',
            7: 'id',
            8: 'num_comments',
        }

        return self.__do_list('airport', kw, airport=airport, columns=columns)

    @without_trailing_slash
    @expose('skylines.templates.flights.list')
    @expose('json')
    def pinned(self, *remainder, **kw):
        # Check if we have cookies
        if request.cookies is None:
            redirect('.')

        # Check for the 'pinnedFlights' cookie
        ids = request.cookies.get('SkyLines_pinnedFlights', None)
        if ids is None:
            redirect('.')

        try:
            # Split the string into integer IDs (%2C = comma)
            ids = [int(id) for id in ids.split('%2C')]
        except ValueError:
            raise HTTPNotFound

        return self.__do_list('pinned', kw, pinned=ids)

    @expose()
    def multi(self, ids):
        return redirect('/flights/' + ids + '/')

    @without_trailing_slash
    @expose()
    @require(has_permission('manage'))
    def analysis(self):
        """Hidden method that restarts flight analysis."""

        for flight in DBSession.query(Flight).options(joinedload(Flight.igc_file)):
            analyse_flight(flight)
            DBSession.flush()

        return redirect('.')

    @without_trailing_slash
    @expose()
    @require(has_permission('manage'))
    def igc_headers(self):
        """Hidden method that parses all missing IGC headers."""
        igc_files = DBSession.query(IGCFile)
        igc_files = igc_files.filter(or_(IGCFile.logger_manufacturer_id == None,
                                         IGCFile.logger_id == None,
                                         IGCFile.model == None,
                                         IGCFile.registration == None))

        for igc_file in igc_files:
            igc_file.update_igc_headers()

        DBSession.flush()

        return redirect('.')

    upload = UploadController()
