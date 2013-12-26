from flask.ext.script import Manager

from .mark_all_unread import MarkAllUnread

manager = Manager(help="Perform operations related to notifications")
manager.add_command('mark-all-unread', MarkAllUnread())
