from flask import Blueprint, render_template, abort, request, jsonify
from sqlalchemy import func, distinct

from skylines.database import db
from skylines.lib.dbutil import get_requested_record
from skylines.lib.vary import vary_accept
from skylines.model import User, Club, Flight, Airport

statistics_blueprint = Blueprint('statistics', 'skylines')


@statistics_blueprint.route('/')
@statistics_blueprint.route('/<page>/<id>')
@vary_accept
def index(page=None, id=None):
    club = None
    pilot = None
    airport = None
    name = None

    query = db.session.query(Flight.year.label('year'),
                             func.count('*').label('flights'),
                             func.count(distinct(Flight.pilot_id)).label('pilots'),
                             func.sum(Flight.olc_classic_distance).label('distance'),
                             func.sum(Flight.duration).label('duration'))

    pilots_query = db.session.query(func.count(distinct(Flight.pilot_id)))

    if page == 'pilot':
        pilot = get_requested_record(User, id)
        name = unicode(pilot)
        query = query.filter(Flight.pilot_id == pilot.id)

    elif page == 'club':
        club = get_requested_record(Club, id)
        name = unicode(club)
        query = query.filter(Flight.club_id == club.id)
        pilots_query = pilots_query.filter(Flight.club_id == club.id)

    elif page == 'airport':
        airport = get_requested_record(Airport, id)
        name = unicode(airport)
        query = query.filter(Flight.takeoff_airport_id == airport.id)
        pilots_query = pilots_query.filter(Flight.takeoff_airport_id == airport.id)

    elif page is not None:
        abort(404)

    query = query.filter(Flight.is_rankable())

    query = query.group_by(Flight.year).order_by(Flight.year.desc())

    if page == 'pilot':
        sum_pilots = 0
    else:
        sum_pilots = pilots_query.scalar()

    list = []
    for row in query:
        row.average_distance = row.distance / row.flights
        row.average_duration = row.duration / row.flights

        list.append({
            'year': row.year,
            'flights': row.flights,
            'distance': row.distance,
            'duration': row.duration.total_seconds(),
            'pilots': row.pilots,
            'average_distance': row.distance / row.flights,
            'average_duration': row.duration.total_seconds() / row.flights,
        })

    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify(name=name, years=list, sumPilots=sum_pilots)

    return render_template('statistics/years.jinja',
                           name=name,
                           years=list,
                           sum_pilots=sum_pilots,
                           airport=airport,
                           pilot=pilot,
                           club=club)
