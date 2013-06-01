#!/usr/bin/env python
#
# Add new admins to a competition
#

import argparse
from config import to_envvar

# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Add new admins to a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    'competition_id', type=int, help='id of the competition')

parser.add_argument(metavar='admin-id', dest='admin_ids',
                    nargs='+', type=int, help='id of the participant')

args = parser.parse_args()

# Load environment

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


import sys
from datetime import datetime
from skylines.model.session import DBSession
from skylines.model import User, Competition

# Load competition

competition = Competition.get(args.competition_id)
if not competition:
    sys.exit('No competition found with id: {}.'.format(args.competition_id))

# Build user list

admins = {u.id: u for u in User.query().filter(User.id.in_(args.admin_ids))}

# Add the admins to the competition

for admin_id in args.admin_ids:

    admin = admins.get(admin_id, None)
    if not admin:
        print 'No user found with id: {}'.format(admin_id)
        continue

    competition.admins.append(admin)
    print 'Added user "{}" (id: {}) to competition with id: {}' \
        .format(admin.name, admin.id, competition.id)

DBSession.commit()
