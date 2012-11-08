from babel.dates import format_date
from datetime import datetime
from tg import expose, require, request, redirect, config
from tg.decorators import with_trailing_slash, without_trailing_slash
from repoze.what.predicates import has_permission
from webob.exc import HTTPNotFound
from sqlalchemy.sql.expression import desc, or_, and_
from sqlalchemy import func
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.orm.util import aliased
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Club, Flight, IGCFile, Airport
from skylines.model.flight_comment import FlightComment
from skylines.controllers.flight import FlightController
from skylines.controllers.upload import UploadController
from skylines.lib.datatables import GetDatatableRecords
from skylines.lib.helpers import truncate
from skylines.lib.dbutil import get_requested_record, get_requested_record_list


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
                    1: 'index_score',
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

        return self.date(date, today=True, **kw)

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
            0: 'index_score',
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

        redirect('pilot/' + str(request.identity['user'].id))

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
            1: 'index_score',
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
            1: 'index_score',
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
            1: 'index_score',
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
    def igc_headers(self, **kwargs):
        """Hidden method that parses all missing IGC headers."""
        igc_files = DBSession.query(IGCFile)
        igc_files = igc_files.filter(or_(IGCFile.logger_manufacturer_id == None,
                                         IGCFile.logger_id == None,
                                         IGCFile.model == None,
                                         IGCFile.registration == None,
                                         IGCFile.competition_id == None))

        for igc_file in igc_files:
            igc_file.update_igc_headers()

        DBSession.flush()

        return redirect('.')

    upload = UploadController()
