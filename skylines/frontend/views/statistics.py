from flask import Blueprint, render_template, abort
from sqlalchemy import func, distinct

from skylines.database import db
from skylines.lib.dbutil import get_requested_record
from skylines.model import User, Club, Flight, Airport

statistics_blueprint = Blueprint('statistics', 'skylines')


@statistics_blueprint.route('/')
@statistics_blueprint.route('/<page>/<id>')
def index(page=None, id=None):
    club = None
    pilot = None
    airport = None

    query = db.session.query(Flight.year.label('year'),
                             func.count('*').label('flights'),
                             func.count(distinct(Flight.pilot_id)).label('pilots'),
                             func.sum(Flight.olc_classic_distance).label('distance'),
                             func.sum(Flight.duration).label('duration'))

    pilots_query = db.session.query(func.count(distinct(Flight.pilot_id)))

    if page == 'pilot':
        pilot = get_requested_record(User, id)
        query = query.filter(Flight.pilot_id == pilot.id)

    elif page == 'club':
        club = get_requested_record(Club, id)
        query = query.filter(Flight.club_id == club.id)
        pilots_query = pilots_query.filter(Flight.club_id == club.id)

    elif page == 'airport':
        airport = get_requested_record(Airport, id)
        query = query.filter(Flight.takeoff_airport_id == airport.id)
        pilots_query = pilots_query.filter(Flight.takeoff_airport_id == airport.id)

    elif page is not None:
        abort(404)

    query = query.filter(Flight.is_rankable())

    query = query.group_by(Flight.year).order_by(Flight.year.desc())

    max_flights = 1
    max_pilots = 1
    max_distance = 1
    max_duration = 1

    sum_flights = 0
    sum_distance = 0
    sum_duration = 0

    if page == 'pilot':
        sum_pilots = 0
    else:
        sum_pilots = pilots_query.scalar()

    list = []
    for row in query:
        row.average_distance = row.distance / row.flights
        row.average_duration = row.duration / row.flights

        list.append(row)

        max_flights = max(max_flights, row.flights)
        max_pilots = max(max_pilots, row.pilots)
        max_distance = max(max_distance, row.distance)
        max_duration = max(max_duration, row.duration.total_seconds())

        sum_flights = sum_flights + row.flights
        sum_distance = sum_distance + row.distance
        sum_duration = sum_duration + row.duration.total_seconds()

    return render_template('statistics/years.jinja',
                           years=list,
                           max_flights=max_flights,
                           max_pilots=max_pilots,
                           max_distance=max_distance,
                           max_duration=max_duration,
                           sum_flights=sum_flights,
                           sum_distance=sum_distance,
                           sum_duration=sum_duration,
                           sum_pilots=sum_pilots,
                           airport=airport,
                           pilot=pilot,
                           club=club)
