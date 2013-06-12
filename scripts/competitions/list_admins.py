#!/usr/bin/env python
#
# List all admins of a competition
#

import argparse
from config import to_envvar

# Parse command line parameters

parser = argparse.ArgumentParser(
    description='List all admins of a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    'competition_id', type=int, help='id of the competition')

args = parser.parse_args()

# Load environment

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


import sys
from skylines.model import Competition

# List participants of the competition

competition = Competition.get(args.competition_id)
if not competition:
    sys.exit('No competition found with id: {}.'.format(args.competition_id))

admins = sorted(competition.admins, key=str)


def print_admin(admin):
    output = '{} (id: {})'.format(admin.name.encode('utf8'), admin.id)
    print output

map(print_admin, admins)
