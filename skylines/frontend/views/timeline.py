from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.orm import subqueryload, contains_eager
from sqlalchemy.sql.expression import or_

from skylines.lib.vary import vary_accept
from skylines.model.event import Event
from skylines.model import Flight
from .notifications import _filter_query

timeline_blueprint = Blueprint('timeline', 'skylines')

TYPES = {
    Event.Type.FLIGHT_COMMENT: 'flight-comment',
    Event.Type.FLIGHT: 'flight-upload',
    Event.Type.FOLLOWER: 'follower',
    Event.Type.NEW_USER: 'new-user',
    Event.Type.CLUB_JOIN: 'club-join',
}


@timeline_blueprint.route('/')
@vary_accept
def index():
    if 'application/json' not in request.headers.get('Accept', ''):
        return render_template('ember-page.jinja')

    query = Event.query() \
        .options(subqueryload('actor')) \
        .options(subqueryload('user')) \
        .options(subqueryload('club')) \
        .outerjoin(Event.flight) \
        .options(contains_eager(Event.flight)) \
        .filter(or_(Event.flight == None, Flight.is_rankable())) \
        .order_by(Event.time.desc())

    query = _filter_query(query, request.args)

    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=50)

    events = query.limit(per_page).offset((page - 1) * per_page).all()

    events_json = []
    for e in events:
        event = {
            'id': e.id,
            'type': TYPES.get(e.type, 'unknown'),
            'time': e.time.isoformat(),
            'actor': {
                'id': e.actor_id,
                'name': unicode(e.actor),
            },
        }

        if e.user_id:
            event['user'] = {
                'id': e.user_id,
                'name': unicode(e.user),
            }

        if e.club_id:
            event['club'] = {
                'id': e.club_id,
                'name': unicode(e.club),
            }

        if e.flight_id:
            event['flight'] = {
                'id': e.flight_id,
                'date': e.flight.date_local.isoformat(),
                'distance': e.flight.olc_classic_distance,
                'pilot_id': e.flight.pilot_id,
                'copilot_id': e.flight.co_pilot_id,
            }

        if e.flight_comment_id:
            event['flightComment'] = {
                'id': e.flight_comment_id,
            }

        events_json.append(event)

    return jsonify(events=events_json)
