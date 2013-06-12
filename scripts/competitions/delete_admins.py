#!/usr/bin/env python
#
# Deletes admins from a competition
#

import argparse
from config import to_envvar

# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Deletes admins from a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    metavar='competition-id', dest='competition_id', type=int,
    help='id of the competition')

parser.add_argument(
    metavar='admin-id', dest='admin_ids', nargs='*', type=int,
    help='id of the admin')

parser.add_argument('--all', action='store_true',
                    help='delete all admins from the competition')

args = parser.parse_args()

# Check --all or participant_ids are available

if not (bool(args.all) ^ bool(args.admin_ids)):
    parser.error('You have to use either --all or specify one or more admin ids.')

# Load environment

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


import sys
from skylines import db
from skylines.model import Competition

# Load competition

competition = Competition.get(args.competition_id)
if not competition:
    sys.exit('No competition found with id: {}.'.format(args.competition_id))

# Delete all admins from the competition

if args.all:
    competition.admins = []

# .. or delete specific admin from the competition

elif args.admin_ids:
    admins = [a for a in competition.admins if a.id in args.admin_ids]
    for admin in admins:
        competition.admins.remove(admin)

        print 'Admin "{}" with id: {} got removed from competition with id: {}.' \
            .format(admin.name, admin.id, args.competition_id)

db.session.commit()
