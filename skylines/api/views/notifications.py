from flask import Blueprint, request
from sqlalchemy.orm import subqueryload, contains_eager
from sqlalchemy.sql.expression import or_

from skylines.api.json import jsonify
from skylines.database import db
from skylines.api.oauth import oauth
from skylines.model import Event, Notification, Flight, User

TYPES = {
    Event.Type.FLIGHT_COMMENT: 'flight-comment',
    Event.Type.FLIGHT: 'flight-upload',
    Event.Type.FOLLOWER: 'follower',
    Event.Type.NEW_USER: 'new-user',
    Event.Type.CLUB_JOIN: 'club-join',
}

notifications_blueprint = Blueprint('notifications', 'skylines')


def _filter_query(query, args):
    type_ = args.get('type', type=int)
    if type_:
        query = query.filter(Event.type == type_)

    user = args.get('user', type=int)
    if user:
        query = query.filter(Event.actor_id == user)

    return query


@notifications_blueprint.route('/notifications', strict_slashes=False)
@oauth.required()
def list():
    query = Notification.query(recipient_id=request.user_id) \
        .join('event') \
        .options(contains_eager('event')) \
        .options(subqueryload('event.actor')) \
        .outerjoin(Event.flight) \
        .options(contains_eager('event.flight')) \
        .filter(or_(Event.flight == None, Flight.is_rankable())) \
        .order_by(Event.time.desc())

    query = _filter_query(query, request.args)

    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=50)

    query = query.limit(per_page)
    query = query.offset((page - 1) * per_page)

    def get_event(notification):
        event = notification.event
        event.unread = (notification.time_read is None)
        return event

    events = map(get_event, query)

    return jsonify(events=(map(convert_event, events)))


@notifications_blueprint.route('/notifications/clear', methods=('POST',))
@oauth.required()
def clear():
    def filter_func(query):
        return _filter_query(query, request.args)

    current_user = User.get(request.user_id)
    Notification.mark_all_read(current_user, filter_func=filter_func)

    db.session.commit()

    return jsonify()


def convert_event(e):
    event = {
        'id': e.id,
        'type': TYPES.get(e.type, 'unknown'),
        'time': e.time.isoformat(),
        'actor': {
            'id': e.actor_id,
            'name': unicode(e.actor),
        },
    }

    if hasattr(e, 'unread'):
        event['unread'] = e.unread

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

    return event
