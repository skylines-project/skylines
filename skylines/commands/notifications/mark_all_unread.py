from flask.ext.script import Command
from skylines.database import db
from skylines.model import Notification


class MarkAllUnread(Command):
    """ Mark all notifications as unread """

    def run(self):
        Notification.query().update(dict(time_read=None))
        db.session.commit()
