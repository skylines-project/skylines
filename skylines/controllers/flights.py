# -*- coding: utf-8 -*-

import math
import logging
from babel.dates import format_date
from datetime import datetime, timedelta
from tg import expose, validate, require, request, redirect, config, flash
from tg.i18n import ugettext as _
from tg.decorators import override_template
from repoze.what.predicates import has_permission
from webob.exc import HTTPNotFound, HTTPForbidden, HTTPServerError
from sqlalchemy.sql.expression import desc, or_, and_, between
from sqlalchemy import func
from tw.forms.fields import TextField
from sprox.formbase import EditableForm
from sprox.widgets import PropertySingleSelectField
from skylines.lib.base import BaseController
from skylines import files
from skylines.model import DBSession, User, Club, Flight, IGCFile, Model, Airport
from skylines.model.flight_comment import FlightComment
from skylines.controllers.upload import UploadController
from skylines.lib.datatables import GetDatatableRecords
from skylines.lib.analysis import analyse_flight, flight_path
from skylines.lib.helpers import truncate
from skylines.lib.dbutil import get_requested_record, get_requested_record_list
from skylines.form import BootstrapForm
from skylinespolyencode import SkyLinesPolyEncoder

log = logging.getLogger(__name__)


class PilotSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        users = DBSession.query(User) \
                .filter(User.club_id == request.identity['user'].club_id) \
                .order_by(User.display_name)
        options = [(None, 'None')] + \
                  [(user.user_id, user) for user in users]
        d['options'] = options
        return d


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
        models = DBSession.query(Model) \
                .order_by(Model.name)
        options = [(None, '[unspecified]')] + \
                  [(model.id, model) for model in models]
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
    contests = [ dict( contest_type = 'olc_plus', trace_type = 'triangle' ),
                 dict( contest_type = 'olc_plus', trace_type = 'classic' ) ]

    contest_traces = []

    for contest in contests:
        contest_trace = flight.get_optimised_contest_trace(contest['contest_type'], contest['trace_type'])
        if not contest_trace: continue

        fixes = map(lambda x: (x.longitude, x.latitude), contest_trace.locations)
        times = []
        for time in contest_trace.times:
            times.append(flight.takeoff_time.hour * 3600 + flight.takeoff_time.minute * 60 + flight.takeoff_time.second + \
                         (time - flight.takeoff_time).days * 86400 + (time - flight.takeoff_time).seconds)

        contest_traces.append( dict( name = contest['contest_type'] + " " + contest['trace_type'],
                                     turnpoints = encoder.encode(fixes, [0]*len(fixes))['points'],
                                     times = encoder.encodeList(times) ) )

    return contest_traces

class FlightController(BaseController):
    def __init__(self, flight):
        if isinstance(flight, list):
            self.flight = flight[0]
            self.other_flights = flight[1:]
        else:
            self.flight = flight
            self.other_flights = None

    def __get_flight_path(self, **kw):
        return get_flight_path(self.flight, **kw)

    @expose('skylines.templates.flights.view')
    def index(self):
        def add_flight_path(flight):
            trace = get_flight_path(flight)
            return (flight, trace)

        other_flights = map(add_flight_path, self.other_flights)
        return dict(flight=self.flight, trace=self.__get_flight_path(), other_flights=other_flights)

    @expose('skylines.templates.flights.map')
    def map(self):
        def add_flight_path(flight):
            trace = get_flight_path(flight, threshold=0.0001, max_points=10000)
            return (flight, trace)

        other_flights = map(add_flight_path, self.other_flights)
        return dict(flight=self.flight, trace=self.__get_flight_path(threshold=0.0001, max_points=10000),
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

    @expose('skylines.templates.generic.form')
    def change_pilot(self):
        if not self.flight.is_writable():
            raise HTTPForbidden

        return dict(page='settings', title=_('Select Pilot'),
                    user=request.identity['user'],
                    include_after='flights/after_change_pilot.html',
                    form=select_pilot_form,
                    values=dict(pilot=self.flight.pilot_id, co_pilot=self.flight.co_pilot_id))

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

    @expose()
    @require(has_permission('upload'))
    def analysis(self):
        """Hidden method that restarts flight analysis."""

        analyse_flight(self.flight)
        DBSession.flush()

        return redirect('.')

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

    @expose()
    def add_comment(self, text):
        if request.identity is None:
            flash(_('You have to be logged in to post comments!'), 'warning')
        else:
            comment = FlightComment()
            comment.user = request.identity['user']
            comment.flight = self.flight
            comment.text = text

        redirect('.')


class FlightsController(BaseController):
    def __do_list(self, tab, kw, date=None, pilot=None, club=None, airport=None, \
                  pinned=None, filter=None, columns=None):
        flights = DBSession.query(Flight) \
            .outerjoin(Flight.pilot) \
            .outerjoin(Flight.igc_file) \
            .outerjoin(Flight.takeoff_airport) \
            .outerjoin(Flight.model)

        if date:
            flights = flights.filter(between(Flight.takeoff_time,
                                             date, date + timedelta(days=1)))
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
                    0: 'takeoff_time',
                    1: 'olc_plus_score',
                    2: 'display_name',
                    3: 'olc_classic_distance',
                    4: 'airports.name',
                    5: 'flights.club_id',
                    6: 'models.name',
                    7: 'takeoff_time',
                    8: 'id'
                }

            flights, response_dict = GetDatatableRecords(kw, flights, columns)

            aaData = []
            for flight in flights:
              aaData.append(dict(takeoff_time = flight.takeoff_time.strftime('%H:%M'),
                                 landing_time = flight.landing_time.strftime('%H:%M'),
                                 date = flight.takeoff_time.strftime('%d.%m.%Y'),
                                 date_formatted = format_date(flight.takeoff_time),
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
                                 flight_id = flight.id))

            return dict(response_dict, aaData = aaData)

        else:
            if date:
                flights = flights.order_by(desc(Flight.olc_plus_score))
            else:
                flights = flights.order_by(desc(Flight.takeoff_time))

            flights_count = flights.count()
            if flights_count > int(config.get('skylines.lists.server_side', 250)):
                limit = int(config.get('skylines.lists.display_length', 50))
            else:
                limit = int(config.get('skylines.lists.server_side', 250))

            flights = flights.order_by(desc(Flight.takeoff_time)).limit(limit)
            return dict(tab = tab, date=date, pilot=pilot, club=club, airport=airport,
                        flights = flights, flights_count = flights_count)

    @expose()
    def lookup(self, id, *remainder):
        # Fallback for old URLs
        if id == 'id' and len(remainder) > 0:
            id = remainder[0]
            remainder = remainder[1:]

        flights = get_requested_record_list(Flight, id)
        controller = FlightController(flights)
        return controller, remainder

    @expose()
    def index(self, **kw):
        redirect('today')

    @expose('skylines.templates.flights.list')
    @expose('json')
    def all(self, **kw):
        return self.__do_list('all', kw)

    @expose('skylines.templates.flights.list')
    @expose('json')
    def today(self, **kw):
        query = DBSession.query(Flight).filter(Flight.takeoff_time < datetime.utcnow())
        query = query.from_self(func.max(Flight.takeoff_time).label('date'))
        date = query.one().date
        if not date:
            raise HTTPNotFound

        return self.date(date, today = True, **kw)

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
            1: 'display_name',
            2: 'olc_classic_distance',
            3: 'airports.name',
            4: 'flights.club_id',
            5: 'models.name',
            6: 'takeoff_time',
            7: 'id',
        }

        if kw.get('today', False):
            return self.__do_list('today', kw, date=date, columns=columns)
        else:
            return self.__do_list('date', kw, date=date, columns=columns)

    @expose()
    def my(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        redirect('/flights/pilot/' + str(request.identity['user'].user_id))

    @expose()
    def my_club(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        redirect('/flights/club/' + str(request.identity['user'].club.id))

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
            0: 'takeoff_time',
            1: 'olc_plus_score',
            2: 'display_name',
            3: 'olc_classic_distance',
            4: 'airports.name',
            5: 'models.name',
            6: 'takeoff_time',
            7: 'id',
        }

        return self.__do_list('pilot', kw, pilot=pilot, columns=columns)

    @expose('skylines.templates.flights.list')
    @expose('json')
    def club(self, id, **kw):
        club = get_requested_record(Club, id)

        columns = {
            0: 'takeoff_time',
            1: 'olc_plus_score',
            2: 'display_name',
            3: 'olc_classic_distance',
            4: 'airports.name',
            5: 'models.name',
            6: 'takeoff_time',
            7: 'id'
        }

        return self.__do_list('club', kw, club=club, columns=columns)

    @expose('skylines.templates.flights.list')
    @expose('json')
    def airport(self, id, **kw):
        airport = get_requested_record(Airport, id)

        columns = {
            0: 'takeoff_time',
            1: 'olc_plus_score',
            2: 'display_name',
            3: 'olc_classic_distance',
            4: 'flights.club_id',
            5: 'models.name',
            6: 'takeoff_time',
            7: 'id'
        }

        return self.__do_list('airport', kw, airport=airport, columns=columns)

    @expose('skylines.templates.flights.list')
    @expose('json')
    def pinned(self, id, **kw):
        ids = list()
        for unique_id in id.split(','):
            try:
                unique_id = int(unique_id)
            except ValueError:
                raise HTTPNotFound

            if unique_id not in ids:
                ids.append(unique_id)

        return self.__do_list('pinned', kw, pinned=ids)

    @expose()
    def multi(self, ids):
        return redirect('/flights/' + ids + '/')

    @expose()
    @require(has_permission('manage'))
    def analysis(self):
        """Hidden method that restarts flight analysis."""

        for flight in DBSession.query(Flight):
            analyse_flight(flight)
            DBSession.flush()

        return redirect('/flights/')

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

        return redirect('/flights/')

    upload = UploadController()
