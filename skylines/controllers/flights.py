from datetime import datetime

from tg import expose, require, request, redirect, config
from tg.decorators import with_trailing_slash, without_trailing_slash
from babel.dates import format_date
from repoze.what.predicates import has_permission
from webob.exc import HTTPNotFound

from sqlalchemy.sql.expression import desc, or_, and_
from sqlalchemy import func
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.orm.util import aliased

from .base import BaseController
from .flight import FlightController
from .upload import UploadController
from skylines.lib.datatables import GetDatatableRecords
from skylines.lib.dbutil import get_requested_record, get_requested_record_list
from skylines.lib.helpers import truncate, country_name
from skylines.model import (
    DBSession, User, Club, Flight, IGCFile, AircraftModel,
    Airport, FlightComment
)


class FlightsController(BaseController):
    def __do_list(self, tab, kw, date=None, pilot=None, club=None, airport=None,
                  pinned=None, filter=None, columns=None):
        pilot_alias = aliased(User, name='pilot')
        owner_alias = aliased(User, name='owner')

        subq = DBSession \
            .query(FlightComment.flight_id, func.count('*').label('count')) \
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
                    0: (Flight, 'date_local'),
                    1: (Flight, 'index_score'),
                    2: (pilot_alias, 'display_name'),
                    3: (Flight, 'olc_classic_distance'),
                    4: (Airport, 'name'),
                    5: (Club, 'name'),
                    6: (AircraftModel, 'name'),
                    7: (Flight, 'takeoff_time'),
                    8: (Flight, 'id'),
                    9: (Flight, 'num_comments'),
                }

            flights, response_dict = GetDatatableRecords(kw, flights, columns)

            aaData = []
            for flight, num_comments in flights:
                aaData.append(dict(takeoff_time=flight.takeoff_time.strftime('%H:%M'),
                                   landing_time=flight.landing_time.strftime('%H:%M'),
                                   date=flight.date_local.strftime('%d.%m.%Y'),
                                   date_formatted=format_date(flight.date_local),
                                   index_score=flight.index_score,
                                   olc_classic_distance=flight.olc_classic_distance,
                                   pilot_id=flight.pilot_id,
                                   pilot=flight.pilot and flight.pilot.display_name,
                                   co_pilot_id=flight.co_pilot_id,
                                   co_pilot=flight.co_pilot and flight.co_pilot.display_name,
                                   club_id=flight.club_id,
                                   club=flight.club and truncate(flight.club.name, 25),
                                   owner=flight.igc_file.owner.display_name,
                                   takeoff_airport=flight.takeoff_airport and flight.takeoff_airport.name,
                                   takeoff_airport_id=flight.takeoff_airport and flight.takeoff_airport.id,
                                   takeoff_airport_country_code=flight.takeoff_airport and flight.takeoff_airport.country_code.lower(),
                                   takeoff_airport_country_name=flight.takeoff_airport and country_name(flight.takeoff_airport.country_code),
                                   aircraft=(flight.model and flight.model.name) or (flight.igc_file.model and '[' + flight.igc_file.model + ']'),
                                   aircraft_reg=flight.registration or flight.igc_file.registration or "Unknown",
                                   flight_id=flight.id,
                                   num_comments=num_comments))

            return dict(response_dict, aaData=aaData)

        else:
            if not date:
                flights = flights.order_by(desc(Flight.date_local))

            flights_count = flights.count()
            if flights_count > int(config.get('skylines.lists.server_side', 250)):
                limit = int(config.get('skylines.lists.display_length', 50))
            else:
                limit = int(config.get('skylines.lists.server_side', 250))

            flights = flights.order_by(desc(Flight.index_score))
            flights = flights.limit(limit)
            return dict(tab=tab, date=date, pilot=pilot, club=club, airport=airport,
                        flights=flights, flights_count=flights_count)

    @expose()
    def _lookup(self, id, *remainder):
        flights = get_requested_record_list(Flight, id,
                                            joinedload=[Flight.igc_file])
        controller = FlightController(flights)
        return controller, remainder

    @with_trailing_slash
    @expose()
    def index(self, **kw):
        redirect('latest')

    @without_trailing_slash
    @expose()
    def today(self, **kw):
        """ Fallback for old /flights/today url """
        redirect('latest')

    @without_trailing_slash
    @expose('flights/list.jinja')
    @expose('json')
    def all(self, **kw):
        return self.__do_list('all', kw)

    @without_trailing_slash
    @expose('flights/list.jinja')
    @expose('json')
    def latest(self, **kw):
        query = DBSession.query(func.max(Flight.date_local).label('date')) \
                         .filter(Flight.takeoff_time < datetime.utcnow())

        date = query.one().date
        if not date:
            date = datetime.utcnow()

        return self.date(date, latest=True, **kw)

    @without_trailing_slash
    @expose('flights/list.jinja')
    @expose('json')
    def date(self, date, **kw):
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, "%Y-%m-%d")

            if isinstance(date, datetime):
                date = date.date()
        except:
            raise HTTPNotFound

        pilot_alias = aliased(User, name='pilot')

        columns = {
            0: (Flight, 'index_score'),
            1: (pilot_alias, 'display_name'),
            2: (Flight, 'olc_classic_distance'),
            3: (Airport, 'name'),
            4: (Club, 'name'),
            5: (AircraftModel, 'name'),
            6: (Flight, 'takeoff_time'),
            7: (Flight, 'id'),
            8: (Flight, 'num_comments'),
        }

        if kw.get('latest', False):
            return self.__do_list('latest', kw, date=date, columns=columns)
        else:
            return self.__do_list('date', kw, date=date, columns=columns)

    @without_trailing_slash
    @expose()
    def my(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        redirect('pilot/' + str(request.identity['user'].id))

    @without_trailing_slash
    @expose()
    def my_club(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        redirect('club/' + str(request.identity['user'].club.id))

    @without_trailing_slash
    @expose('flights/list.jinja')
    @expose('json')
    def unassigned(self, **kw):
        if not request.identity:
            raise HTTPNotFound

        f = and_(Flight.pilot_id is None,
                 IGCFile.owner == request.identity['user'])
        return self.__do_list('unassigned', kw, filter=f)

    @expose('flights/list.jinja')
    @expose('json')
    def pilot(self, id, **kw):
        pilot = get_requested_record(User, id)
        pilot_alias = aliased(User, name='pilot')

        columns = {
            0: (Flight, 'date_local'),
            1: (Flight, 'index_score'),
            2: (pilot_alias, 'display_name'),
            3: (Flight, 'olc_classic_distance'),
            4: (Airport, 'name'),
            5: (AircraftModel, 'name'),
            6: (Flight, 'takeoff_time'),
            7: (Flight, 'id'),
            8: (Flight, 'num_comments'),
        }

        return self.__do_list('pilot', kw, pilot=pilot, columns=columns)

    @expose('flights/list.jinja')
    @expose('json')
    def club(self, id, **kw):
        club = get_requested_record(Club, id)
        pilot_alias = aliased(User, name='pilot')

        columns = {
            0: (Flight, 'date_local'),
            1: (Flight, 'index_score'),
            2: (pilot_alias, 'display_name'),
            3: (Flight, 'olc_classic_distance'),
            4: (Airport, 'name'),
            5: (AircraftModel, 'name'),
            6: (Flight, 'takeoff_time'),
            7: (Flight, 'id'),
            8: (Flight, 'num_comments'),
        }

        return self.__do_list('club', kw, club=club, columns=columns)

    @expose('flights/list.jinja')
    @expose('json')
    def airport(self, id, **kw):
        airport = get_requested_record(Airport, id)
        pilot_alias = aliased(User, name='pilot')

        columns = {
            0: (Flight, 'date_local'),
            1: (Flight, 'index_score'),
            2: (pilot_alias, 'display_name'),
            3: (Flight, 'olc_classic_distance'),
            4: (Club, 'name'),
            5: (AircraftModel, 'name'),
            6: (Flight, 'takeoff_time'),
            7: (Flight, 'id'),
            8: (Flight, 'num_comments'),
        }

        return self.__do_list('airport', kw, airport=airport, columns=columns)

    @without_trailing_slash
    @expose('flights/list.jinja')
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

    @without_trailing_slash
    @expose()
    @require(has_permission('manage'))
    def igc_headers(self, **kwargs):
        """Hidden method that parses all missing IGC headers."""
        igc_files = IGCFile.query().filter(or_(
            IGCFile.logger_manufacturer_id is None,
            IGCFile.logger_id is None,
            IGCFile.model is None,
            IGCFile.registration is None,
            IGCFile.competition_id is None,
            IGCFile.date_utc is None))

        for igc_file in igc_files:
            igc_file.update_igc_headers()

        DBSession.flush()

        return redirect('.')

    upload = UploadController()
