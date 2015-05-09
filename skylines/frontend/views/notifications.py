from flask import Blueprint, render_template, request, url_for, redirect, g
from sqlalchemy.orm import subqueryload, contains_eager
from sqlalchemy.sql.expression import or_

from skylines.lib.util import str_to_bool
from skylines.database import db
from skylines.model.event import Event, Notification, Flight, group_events
from skylines.lib.decorators import login_required


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
def index():
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
    events_count = len(events)

    if request.args.get('grouped', True, type=str_to_bool):
        events = group_events(events)

    template_vars = dict(events=events, types=Event.Type)

    if page > 1:
        template_vars['prev_page'] = page - 1
    if events_count == per_page:
        template_vars['next_page'] = page + 1

    return render_template('notifications/list.jinja', **template_vars)


@notifications_blueprint.route('/clear')
@login_required("You have to login to clear notifications.")
def clear():
    def filter_func(query):
        return _filter_query(query, request.args)

    Notification.mark_all_read(g.current_user, filter_func=filter_func)

    db.session.commit()

    return redirect(url_for('.index', **request.args))
