from flask import Blueprint, render_template, request, url_for, redirect, g, jsonify, abort
from sqlalchemy.orm import subqueryload, contains_eager
from sqlalchemy.sql.expression import or_

from skylines.lib.vary import vary_accept
from skylines.database import db
from skylines.model.event import Event, Notification, Flight, group_events
from skylines.lib.decorators import login_required

TYPES = {
    Event.Type.FLIGHT_COMMENT: 'flight-comment',
    Event.Type.FLIGHT: 'flight-upload',
    Event.Type.FOLLOWER: 'follower',
    Event.Type.NEW_USER: 'new-user',
    Event.Type.CLUB_JOIN: 'club-join',
}

notifications_blueprint = Blueprint('notifications', 'skylines')


@notifications_blueprint.before_app_request
def inject_notification_count():
    if g.current_user:
        def count_unread_notifications():
            return Notification.count_unread(g.current_user)

        g.count_unread_notifications = count_unread_notifications


@notifications_blueprint.before_request
def before_request():
    if g.current_user:
        g.logout_next = url_for("index")


def _filter_query(query, args):
    type_ = args.get('type', type=int)
    if type_:
        query = query.filter(Event.type == type_)

    user = args.get('user', type=int)
    if user:
        query = query.filter(Event.actor_id == user)

    return query


@notifications_blueprint.route('/')
@login_required("You have to login to read notifications.")
@vary_accept
def index():
    if 'application/json' not in request.headers.get('Accept', ''):
        return render_template('ember-page.jinja', active_page='notifications')

    query = Notification.query(recipient=g.current_user) \
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


@notifications_blueprint.route('/clear', methods=['GET', 'POST'])
@login_required("You have to login to clear notifications.")
@vary_accept
def clear():
    def filter_func(query):
        return _filter_query(query, request.args)

    Notification.mark_all_read(g.current_user, filter_func=filter_func)

    db.session.commit()

    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify()

    return redirect(url_for('.index', **request.args))


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
