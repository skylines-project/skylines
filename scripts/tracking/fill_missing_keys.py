#!/usr/bin/env python
#
# Generate tracking keys for user accounts that don't have one
#

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(
    description='Generate tracking keys for user accounts that don\'t have one.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from skylines import db
from skylines.model import User


keyless_users = User.query(tracking_key=None)

for i, user in enumerate(keyless_users):
    user.generate_tracking_key()

    if i % 25 == 0:
        db.session.flush()

db.session.commit()
