#!/usr/bin/env python
#
# List all competitions
#

import argparse
from config import to_envvar

# Parse command line parameters

parser = argparse.ArgumentParser(
    description='List all competitions.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument('--only-running', action='store_true',
                    help='only competitions are returned that are currently running')

parser.add_argument('--only-upcoming', action='store_true',
                    help='only competitions in the future are returned')

parser.add_argument('--only-past', action='store_true',
                    help='only competitions in the past are returned')

args = parser.parse_args()

# Load environment

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from datetime import datetime
from skylines.model import Competition

# List participants of the competition

query = Competition.query() \
    .order_by(Competition.start_date.desc(), Competition.end_date.desc())

if args.only_running:
    query = query \
        .filter(Competition.start_date <= datetime.utcnow()) \
        .filter(Competition.end_date >= datetime.utcnow())

if args.only_upcoming:
    query = query.filter(Competition.start_date > datetime.utcnow())

if args.only_past:
    query = query.filter(Competition.end_date < datetime.utcnow())


def print_competition(competition):
    output = '{} (id: {}), start: {}, end: {}'.format(
        competition.name.encode('utf8'), competition.id,
        competition.start_date, competition.end_date)

    print output

map(print_competition, query)
