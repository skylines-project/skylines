from collections import defaultdict
from operator import itemgetter

from tg import expose, request, redirect
from tg.decorators import with_trailing_slash, without_trailing_slash
from webob.exc import HTTPForbidden, HTTPNotImplemented
from sqlalchemy.orm import joinedload, contains_eager

from .base import BaseController
from skylines.lib.dbutil import get_requested_record
from skylines.model import Event, Notification


class NotificationController(BaseController):
    def __init__(self, notification):
        self.notification = notification

    @expose()
    def index(self, **kwargs):
        self.notification.mark_read()

        event = self.notification.event

        if event.type == Event.Type.FLIGHT_COMMENT:
            redirect('/flights/{}/'.format(event.flight_id))
        elif event.type == Event.Type.FLIGHT:
            redirect('/flights/{}/'.format(event.flight_id))
        elif event.type == Event.Type.FOLLOWER:
            redirect('/users/{}/'.format(event.actor_id))
        else:
            raise HTTPNotImplemented


class NotificationsController(BaseController):
    def __filter_query(self, query, args):
        if 'type' in args:
            query = query.filter(Event.type == args['type'])
        if 'sender' in args:
            query = query.filter(Event.actor_id == args['sender'])
        if 'flight' in args:
            query = query.filter(Event.flight_id == args['flight'])

        return query

    @expose()
    def _lookup(self, id, *remainder):
        if not request.identity:
            raise HTTPForbidden

        notification = get_requested_record(Notification, id)
        if request.identity['user'] != notification.recipient:
            raise HTTPForbidden

        controller = NotificationController(notification)
        return controller, remainder

    @with_trailing_slash
    @expose('notifications/list.jinja')
    def index(self, **kwargs):
        if not request.identity:
            raise HTTPForbidden

        query = Notification.query_unread(request.identity['user']) \
            .join('event') \
            .options(contains_eager('event')) \
            .options(joinedload('event.actor')) \
            .options(joinedload('event.flight')) \
            .options(joinedload('event.flight_comment')) \
            .order_by(Event.time.desc())

        query = self.__filter_query(query, kwargs)

        notifications = []
        pilot_flights = defaultdict(list)
        for notification in query:
            event = notification.event

            if (event.type == Event.Type.FLIGHT and 'type' not in kwargs):
                pilot_flights[event.actor_id].append(notification)
            else:
                notifications.append(dict(grouped=False,
                                          id=notification.id,
                                          type=event.type,
                                          time=event.time,
                                          event=event))

        for flights in pilot_flights.itervalues():
            first_notification = flights[0]
            first_event = first_notification.event

            if len(flights) == 1:
                notifications.append(dict(grouped=False,
                                          id=first_notification.id,
                                          type=first_event.type,
                                          time=first_event.time,
                                          event=first_event))
            else:
                notifications.append(dict(grouped=True,
                                          type=first_event.type,
                                          time=first_event.time,
                                          events=[n.event for n in flights]))

        notifications.sort(key=itemgetter('time'), reverse=True)

        return dict(notifications=notifications, params=kwargs,
                    types=Event.Type)

    @without_trailing_slash
    @expose()
    def clear(self, **kwargs):
        if not request.identity:
            raise HTTPForbidden

        def filter_func(query):
            return self.__filter_query(query, kwargs)

        Notification.mark_all_read(request.identity['user'],
                                   filter_func=filter_func)

        redirect('.')
