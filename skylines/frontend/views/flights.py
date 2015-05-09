from datetime import datetime

from flask import Blueprint, request, render_template, redirect, url_for, abort, current_app, g

from sqlalchemy import func
from sqlalchemy.sql.expression import or_, and_
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.orm.util import aliased

from skylines.database import db
from skylines.lib.table_tools import Pager, Sorter
from skylines.lib.dbutil import get_requested_record
from skylines.model import (
    User, Club, Flight, IGCFile, AircraftModel,
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
                 pinned=None, filter=None,
                 default_sorting_column='score', default_sorting_order='desc'):
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

    valid_columns = {
        'date': getattr(Flight, 'date_local'),
        'score': getattr(Flight, 'index_score'),
        'pilot': getattr(pilot_alias, 'name'),
        'distance': getattr(Flight, 'olc_classic_distance'),
        'airport': getattr(Airport, 'name'),
        'club': getattr(Club, 'name'),
        'aircraft': getattr(AircraftModel, 'name'),
        'time': getattr(Flight, 'takeoff_time'),
    }

    flights_count = flights.count()

    flights = Sorter.sort(flights, 'flights', default_sorting_column,
                          valid_columns=valid_columns,
                          default_order=default_sorting_order)

    flights = flights.order_by(Flight.index_score.desc())

    flights = Pager.paginate(flights, 'flights',
                             items_per_page=int(current_app.config.get('SKYLINES_LISTS_DISPLAY_LENGTH', 50)))

    return render_template('flights/list.jinja',
                           tab=tab, date=date, pilot=pilot, club=club,
                           airport=airport, flights=flights,
                           flights_count=flights_count)


@flights_blueprint.route('/all.json')
@flights_blueprint.route('/all')
def all():
    return _create_list('all', request.args,
                        default_sorting_column='date', default_sorting_order='desc')


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

    return _create_list(
        'latest' if latest else 'date',
        request.args, date=date,
        default_sorting_column='score', default_sorting_order='desc')


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

    mark_flight_notifications_read(pilot)

    return _create_list('pilot', request.args, pilot=pilot,
                        default_sorting_column='date', default_sorting_order='desc')


@flights_blueprint.route('/my')
def my():
    if not g.current_user:
        abort(404)

    return redirect(url_for('.pilot', id=g.current_user.id))


@flights_blueprint.route('/club/<int:id>.json')
@flights_blueprint.route('/club/<int:id>')
def club(id):
    club = get_requested_record(Club, id)

    return _create_list('club', request.args, club=club,
                        default_sorting_column='date', default_sorting_order='desc')


@flights_blueprint.route('/my_club')
def my_club():
    if not g.current_user:
        abort(404)

    return redirect(url_for('.club', id=g.current_user.club.id))


@flights_blueprint.route('/airport/<int:id>.json')
@flights_blueprint.route('/airport/<int:id>')
def airport(id):
    airport = get_requested_record(Airport, id)

    return _create_list('airport', request.args,
                        airport=airport,
                        default_sorting_column='date', default_sorting_order='desc')


@flights_blueprint.route('/unassigned.json')
@flights_blueprint.route('/unassigned')
def unassigned():
    if not g.current_user:
        abort(404)

    f = and_(Flight.pilot_id is None,
             IGCFile.owner == g.current_user)

    return _create_list('unassigned', request.args, filter=f,
                        default_sorting_column='date', default_sorting_order='desc')


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

    return _create_list('pinned', request.args, pinned=ids,
                        default_sorting_column='date', default_sorting_order='desc')


@flights_blueprint.route('/list/<ids>.json')
@flights_blueprint.route('/list/<ids>')
def list(ids):
    # Check for the 'pinnedFlights' cookie
    if not ids:
        return redirect(url_for('.index'))

    try:
        # Split the string into integer IDs
        ids = [int(id) for id in ids.split(',')]
    except ValueError:
        abort(404)

    return _create_list('list', request.args, pinned=ids,
                        default_sorting_column='date', default_sorting_order='desc')


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
