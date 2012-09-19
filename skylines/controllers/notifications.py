from tg import expose, request, redirect
from tg.decorators import with_trailing_slash, without_trailing_slash
from webob.exc import HTTPForbidden, HTTPNotImplemented
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import desc

from skylines.lib.base import BaseController
from skylines.lib.dbutil import get_requested_record
from skylines.model import DBSession, Notification


class NotificationController(BaseController):
    def __init__(self, notification):
        self.notification = notification

    @expose()
    def index(self):
        self.notification.mark_read()

        if self.notification.type == Notification.NT_FLIGHT_COMMENT:
            redirect('/flights/{}/'.format(self.notification.flight_id))
        elif self.notification.type == Notification.NT_FLIGHT:
            redirect('/flights/{}/'.format(self.notification.flight_id))
        elif self.notification.type == Notification.NT_FOLLOWER:
            redirect('/users/{}/'.format(self.notification.sender_id))
        else:
            raise HTTPNotImplemented


class NotificationsController(BaseController):
    @expose()
    def lookup(self, id, *remainder):
        if not request.identity:
            raise HTTPForbidden

        notification = get_requested_record(Notification, id)
        if request.identity['user'] != notification.recipient:
            raise HTTPForbidden

        controller = NotificationController(notification)
        return controller, remainder

    @with_trailing_slash
    @expose('skylines.templates.notifications.list')
    def index(self):
        if not request.identity:
            raise HTTPForbidden

        query = DBSession.query(Notification) \
                         .filter(Notification.recipient == request.identity['user']) \
                         .filter(Notification.time_read == None) \
                         .options(joinedload(Notification.sender)) \
                         .options(joinedload(Notification.recipient)) \
                         .options(joinedload(Notification.flight)) \
                         .options(joinedload(Notification.flight_comment)) \
                         .order_by(desc(Notification.time_created))

        return dict(notifications=query.all())

    @without_trailing_slash
    @expose()
    def clear(self):
        if not request.identity:
            raise HTTPForbidden

        Notification.mark_all_read(request.identity['user'])

        redirect('.')
