#!/usr/bin/env python
#
# Clear all live tracks for a certain user.
#

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Clear all live tracks for a certain user.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('user', type=int,
                    help='a user ID')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from skylines import create_app
from skylines.model import db, TrackingFix

app = create_app()
app.app_context().push()

result = TrackingFix.query(pilot_id=args.user).delete()
db.session.commit()

print '%d live tracks cleared.' % result
