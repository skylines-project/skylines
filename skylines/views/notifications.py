from collections import namedtuple
from itertools import imap

from flask import Blueprint, render_template, abort, request, url_for, redirect, g
from sqlalchemy.orm import joinedload, contains_eager

from skylines import db
from skylines.lib.dbutil import get_requested_record
from skylines.model import Event, Notification

EventGroup = namedtuple('EventGroup', ['grouped', 'type', 'time', 'actor_id', 'link', 'events'])


notifications_blueprint = Blueprint('notifications', 'skylines')


@notifications_blueprint.before_app_request
def inject_notification_count():
    if g.current_user:
        g.notifications = Notification.count_unread(g.current_user)


def _filter_query(query, args):
    if 'type' in args:
        query = query.filter(Event.type == args['type'])
    if 'sender' in args:
        query = query.filter(Event.actor_id == args['sender'])
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
                events[-1] = EventGroup(
                    grouped=True, type=event.type, time=last_event.time,
                    actor_id=event.actor_id, events=[last_event, event],
                    link=url_for('.index', type=event.type, sender=event.actor_id))
            continue

        events.append(event)

    return events


@notifications_blueprint.route('/')
def index():
    if not g.current_user:
        abort(401)

    query = Notification.query_unread(g.current_user) \
        .join('event') \
        .options(contains_eager('event')) \
        .options(joinedload('event.actor')) \
        .options(joinedload('event.flight')) \
        .order_by(Event.time.desc())

    query = _filter_query(query, request.args)

    def get_event(notification):
        event = notification.event
        event.link = url_for('.show', id=notification.id)
        return event

    if 'type' in request.args:
        events = map(get_event, query)
    else:
        events = _group_events(imap(get_event, query))

    return render_template('notifications/list.jinja',
                           events=events,
                           params=request.args, types=Event.Type)


@notifications_blueprint.route('/clear')
def clear():
    if not g.current_user:
        abort(401)

    def filter_func(query):
        return _filter_query(query, request.args)

    Notification.mark_all_read(g.current_user, filter_func=filter_func)

    db.session.commit()

    return redirect(url_for('.index'))


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
