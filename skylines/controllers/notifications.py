from tg import expose, request, redirect
from webob.exc import HTTPForbidden
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

        redirect('/flights/{}/'.format(self.notification.flight_id))


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

    @expose()
    def clear(self):
        if not request.identity:
            raise HTTPForbidden

        Notification.mark_all_read(request.identity['user'])

        redirect('/notifications/')
