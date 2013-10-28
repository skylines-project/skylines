from datetime import datetime

from flask import Blueprint, request, render_template, redirect, url_for, abort, current_app, jsonify, g
from babel.dates import format_date

from sqlalchemy import func
from sqlalchemy.sql.expression import or_, and_
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.orm.util import aliased

from skylines.lib.datatables import GetDatatableRecords
from skylines.lib.dbutil import get_requested_record
from skylines.lib.helpers import truncate, country_name, format_decimal
from skylines.model import (
    db, User, Club, Flight, IGCFile, AircraftModel,
    Airport, FlightComment,
    Notification, Event,
)

flights_blueprint = Blueprint('flights', 'skylines')


def mark_flight_notifications_read(pilot):
    if not g.current_user:
        return

    def add_flight_filter(query):
        return query.filter(Event.actor_id == pilot.id)

    Notification.mark_all_read(g.current_user, filter_func=add_flight_filter)
    db.session.commit()


def _create_list(tab, kw, date=None, pilot=None, club=None, airport=None,
                 pinned=None, filter=None, columns=None):
    pilot_alias = aliased(User, name='pilot')
    owner_alias = aliased(User, name='owner')

    subq = db.session \
        .query(FlightComment.flight_id, func.count('*').label('count')) \
        .group_by(FlightComment.flight_id).subquery()

    flights = db.session.query(Flight, subq.c.count) \
        .filter(Flight.is_listable(g.current_user)) \
        .join(Flight.igc_file) \
        .options(contains_eager(Flight.igc_file)) \
        .join(owner_alias, IGCFile.owner) \
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

    if request.is_xhr:
        if not columns:
            columns = {
                0: (Flight, 'date_local'),
                1: (Flight, 'index_score'),
                2: (pilot_alias, 'name'),
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
                               index_score=format_decimal(flight.index_score, format='0'),
                               olc_classic_distance=flight.olc_classic_distance,
                               pilot_id=flight.pilot_id,
                               pilot=flight.pilot and flight.pilot.name,
                               pilot_name=flight.pilot_name,
                               co_pilot_id=flight.co_pilot_id,
                               co_pilot=flight.co_pilot and flight.co_pilot.name,
                               co_pilot_name=flight.co_pilot_name,
                               club_id=flight.club_id,
                               club=flight.club and truncate(flight.club.name, 25),
                               owner=flight.igc_file.owner.name,
                               takeoff_airport=flight.takeoff_airport and flight.takeoff_airport.name,
                               takeoff_airport_id=flight.takeoff_airport and flight.takeoff_airport.id,
                               takeoff_airport_country_code=flight.takeoff_airport and flight.takeoff_airport.country_code.lower(),
                               takeoff_airport_country_name=flight.takeoff_airport and country_name(flight.takeoff_airport.country_code),
                               aircraft=(flight.model and flight.model.name) or (flight.igc_file.model and '[' + flight.igc_file.model + ']'),
                               aircraft_reg=flight.registration or flight.igc_file.registration or "Unknown",
                               flight_id=flight.id,
                               num_comments=num_comments))

        return jsonify(aaData=aaData, **response_dict)

    else:
        if not date:
            flights = flights.order_by(Flight.date_local.desc())

        flights_count = flights.count()
        if flights_count > int(current_app.config.get('SKYLINES_LISTS_SERVER_SIDE', 250)):
            limit = int(current_app.config.get('SKYLINES_LISTS_DISPLAY_LENGTH', 50))
        else:
            limit = int(current_app.config.get('SKYLINES_LISTS_SERVER_SIDE', 250))

        flights = flights.order_by(Flight.index_score.desc())
        flights = flights.limit(limit)

        return render_template('flights/list.jinja',
                               tab=tab, date=date, pilot=pilot, club=club,
                               airport=airport, flights=flights,
                               flights_count=flights_count)


@flights_blueprint.route('/all.json')
@flights_blueprint.route('/all')
def all():
    return _create_list('all', request.args)


@flights_blueprint.route('/')
def index():
    return redirect(url_for('.latest'))


@flights_blueprint.route('/today')
def today():
    """ Fallback for old /flights/today url """
    return redirect(url_for('.latest'))


@flights_blueprint.route('/date/<date>.json')
@flights_blueprint.route('/date/<date>')
def date(date, latest=False):
    try:
        if isinstance(date, (str, unicode)):
            date = datetime.strptime(date, "%Y-%m-%d")

        if isinstance(date, datetime):
            date = date.date()

    except:
        abort(404)

    pilot_alias = aliased(User, name='pilot')

    columns = {
        0: (Flight, 'index_score'),
        1: (pilot_alias, 'name'),
        2: (Flight, 'olc_classic_distance'),
        3: (Airport, 'name'),
        4: (Club, 'name'),
        5: (AircraftModel, 'name'),
        6: (Flight, 'takeoff_time'),
        7: (Flight, 'id'),
        8: (Flight, 'num_comments'),
    }

    return _create_list(
        'latest' if latest else 'date',
        request.args, date=date, columns=columns)


@flights_blueprint.route('/latest.json')
@flights_blueprint.route('/latest')
def latest():
    query = db.session \
        .query(func.max(Flight.date_local).label('date')) \
        .filter(Flight.takeoff_time < datetime.utcnow()) \
        .join(Flight.igc_file) \
        .filter(Flight.is_listable(g.current_user))

    date_ = query.one().date
    if not date_:
        date_ = datetime.utcnow()

    return date(date_, latest=True)


@flights_blueprint.route('/pilot/<int:id>.json')
@flights_blueprint.route('/pilot/<int:id>')
def pilot(id):
    pilot = get_requested_record(User, id)
    pilot_alias = aliased(User, name='pilot')

    mark_flight_notifications_read(pilot)

    columns = {
        0: (Flight, 'date_local'),
        1: (Flight, 'index_score'),
        2: (pilot_alias, 'name'),
        3: (Flight, 'olc_classic_distance'),
        4: (Airport, 'name'),
        5: (AircraftModel, 'name'),
        6: (Flight, 'takeoff_time'),
        7: (Flight, 'id'),
        8: (Flight, 'num_comments'),
    }

    return _create_list('pilot', request.args, pilot=pilot, columns=columns)


@flights_blueprint.route('/my')
def my():
    if not g.current_user:
        abort(404)

    return redirect(url_for('.pilot', id=g.current_user.id))


@flights_blueprint.route('/club/<int:id>.json')
@flights_blueprint.route('/club/<int:id>')
def club(id):
    club = get_requested_record(Club, id)
    pilot_alias = aliased(User, name='pilot')

    columns = {
        0: (Flight, 'date_local'),
        1: (Flight, 'index_score'),
        2: (pilot_alias, 'name'),
        3: (Flight, 'olc_classic_distance'),
        4: (Airport, 'name'),
        5: (AircraftModel, 'name'),
        6: (Flight, 'takeoff_time'),
        7: (Flight, 'id'),
        8: (Flight, 'num_comments'),
    }

    return _create_list('club', request.args, club=club, columns=columns)


@flights_blueprint.route('/my_club')
def my_club():
    if not g.current_user:
        abort(404)

    return redirect(url_for('.club', id=g.current_user.club.id))


@flights_blueprint.route('/airport/<int:id>.json')
@flights_blueprint.route('/airport/<int:id>')
def airport(id):
    airport = get_requested_record(Airport, id)
    pilot_alias = aliased(User, name='pilot')

    columns = {
        0: (Flight, 'date_local'),
        1: (Flight, 'index_score'),
        2: (pilot_alias, 'name'),
        3: (Flight, 'olc_classic_distance'),
        4: (Club, 'name'),
        5: (AircraftModel, 'name'),
        6: (Flight, 'takeoff_time'),
        7: (Flight, 'id'),
        8: (Flight, 'num_comments'),
    }

    return _create_list('airport', request.args,
                        airport=airport, columns=columns)


@flights_blueprint.route('/unassigned.json')
@flights_blueprint.route('/unassigned')
def unassigned():
    if not g.current_user:
        abort(404)

    f = and_(Flight.pilot_id is None,
             IGCFile.owner == g.current_user)

    return _create_list('unassigned', request.args, filter=f)


@flights_blueprint.route('/pinned.json')
@flights_blueprint.route('/pinned')
def pinned():
    # Check if we have cookies
    if request.cookies is None:
        return redirect(url_for('.index'))

    # Check for the 'pinnedFlights' cookie
    ids = request.cookies.get('SkyLines_pinnedFlights', None)
    if not ids:
        return redirect(url_for('.index'))

    try:
        # Split the string into integer IDs (%2C = comma)
        ids = [int(id) for id in ids.split('%2C')]
    except ValueError:
        abort(404)

    return _create_list('pinned', request.args, pinned=ids)


@flights_blueprint.route('/igc_headers')
def igc_headers():
    """Hidden method that parses all missing IGC headers."""

    if not g.current_user or not g.current_user.is_manager():
        abort(403)

    igc_files = IGCFile.query().filter(or_(
        IGCFile.logger_manufacturer_id is None,
        IGCFile.logger_id is None,
        IGCFile.model is None,
        IGCFile.registration is None,
        IGCFile.competition_id is None,
        IGCFile.date_utc is None))

    for igc_file in igc_files:
        igc_file.update_igc_headers()

    db.session.commit()

    return redirect(url_for('.index'))
