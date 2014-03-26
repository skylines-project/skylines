from flask import Blueprint, g, render_template, request, Response, abort
from werkzeug.exceptions import BadRequest

from sqlalchemy.sql.expression import or_

from skylines.model import User, Club, Flight

widgets_blueprint = Blueprint('widgets', 'skylines')


@widgets_blueprint.route('/')
def index():
    if g.current_user:
        club = g.current_user.club
    else:
        club = Club.get(1)

    return render_template('widgets/index.jinja', club=club)


def wrap(callback, content):
    content = content.replace('\n', '').replace('    ', '')

    return Response(
        render_template('widgets/wrapper.jinja', callback=callback, content=content),
        mimetype='application/javascript; charset=utf-8',
    )


@widgets_blueprint.route('/v1.0/flights.js')
def flights_js():
    flights = Flight.query() \
                    .filter(Flight.is_rankable())

    # Filter by user
    user_id = request.values.get('user', type=int)
    if user_id:
        user = User.get(user_id)
        if not user:
            abort(404)

        flights = flights.filter(or_(
            Flight.pilot == user,
            Flight.co_pilot == user
        ))

    # Filter by club
    club_id = request.values.get('club', type=int)
    if club_id:
        club = Club.get(club_id)
        if not club:
            abort(404)

        flights = flights.filter(Flight.club == club)

    # Order by date and distance
    flights = flights.order_by(Flight.date_local.desc(), Flight.olc_classic_distance)

    # Limit number of flights
    limit = request.values.get('limit', type=int, default=5)
    if not 0 < limit <= 30:
        raise BadRequest('The `limit` parameter must be between 1 and 30.')

    flights = flights.limit(limit)

    # Produce JS response
    callback = request.values.get('callback', 'onFlightsLoaded')
    return wrap(callback, render_template('widgets/flights.jinja', flights=flights))
