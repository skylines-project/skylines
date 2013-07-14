from flask import Blueprint, render_template, abort, request, url_for, redirect, g
from sqlalchemy.orm import joinedload, contains_eager

from skylines import db
from skylines.lib.dbutil import get_requested_record
from skylines.model import Event, Notification


class EventGroup:
    grouped = True

    def __init__(self, events, link=None):
        self.events = events
        self.link = link

    @property
    def unread(self):
        for event in self.events:
            if hasattr(event, 'unread') and event.unread:
                return True

        return False

    def __getattr__(self, name):
        return getattr(self.events[0], name)


notifications_blueprint = Blueprint('notifications', 'skylines')


@notifications_blueprint.before_app_request
def inject_notification_count():
    if g.current_user:
        def count_unread_notifications():
            return Notification.count_unread(g.current_user)

        g.count_unread_notifications = count_unread_notifications


def _filter_query(query, args):
    if 'type' in args:
        query = query.filter(Event.type == args['type'])
    if 'user' in args:
        query = query.filter(Event.actor_id == args['user'])
    if 'flight' in args:
        query = query.filter(Event.flight_id == args['flight'])

    return query


def _group_events(_events):
    events = []
    for event in _events:
        # add first event if list is empty
        if not events:
            events.append(event)
            continue

        # get last event from list for comparison
        last_event = events[-1]

        # if there are multiple flight events from the same actor -> group them
        if (event.type == Event.Type.FLIGHT and
                last_event.type == event.type and
                last_event.actor_id == event.actor_id):
            if isinstance(last_event, EventGroup):
                last_event.events.append(event)
            else:
                events[-1] = EventGroup([last_event, event], link=url_for(
                    '.index', type=event.type, user=event.actor_id))
            continue

        events.append(event)

    return events


@notifications_blueprint.route('/')
def index():
    if not g.current_user:
        abort(401)

    query = Notification.query(recipient=g.current_user) \
        .join('event') \
        .options(contains_eager('event')) \
        .options(joinedload('event.actor')) \
        .options(joinedload('event.flight')) \
        .order_by(Event.time.desc())

    query = _filter_query(query, request.args)

    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=50)

    query = query.limit(per_page)
    query = query.offset((page - 1) * per_page)

    def get_event(notification):
        event = notification.event
        event.link = url_for('.show', id=notification.id)
        event.unread = (notification.time_read is None)
        return event

    events = map(get_event, query)
    events_count = len(events)

    if 'type' not in request.args:
        events = _group_events(events)

    template_vars = dict(events=events, types=Event.Type)

    if page > 1:
        template_vars['prev_page'] = page - 1
    if events_count == per_page:
        template_vars['next_page'] = page + 1

    return render_template('notifications/list.jinja', **template_vars)


@notifications_blueprint.route('/clear')
def clear():
    if not g.current_user:
        abort(401)

    def filter_func(query):
        return _filter_query(query, request.args)

    Notification.mark_all_read(g.current_user, filter_func=filter_func)

    db.session.commit()

    return redirect(url_for('.index', **request.args))


@notifications_blueprint.route('/<int:id>')
def show(id):
    if not g.current_user:
        abort(401)

    notification = get_requested_record(Notification, id)
    if g.current_user != notification.recipient:
        abort(403)

    notification.mark_read()
    db.session.commit()

    event = notification.event

    if event.type == Event.Type.FLIGHT_COMMENT:
        return redirect('/flights/{}/'.format(event.flight_id))
    elif event.type == Event.Type.FLIGHT:
        return redirect('/flights/{}/'.format(event.flight_id))
    elif event.type == Event.Type.FOLLOWER:
        return redirect('/users/{}/'.format(event.actor_id))
    else:
        abort(501)
