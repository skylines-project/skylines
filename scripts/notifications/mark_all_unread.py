#!/usr/bin/env python
#
# Mark all notifications as unread
#

import argparse
from config import to_envvar

parser = argparse.ArgumentParser(description='Copy flight files by one or more properties.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

from skylines import app
from skylines.model import db, Notification

app.app_context().push()

Notification.query().update(dict(time_read=None))

db.session.commit()
