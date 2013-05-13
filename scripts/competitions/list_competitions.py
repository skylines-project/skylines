#!/usr/bin/env python
#
# List all competitions
#

import argparse

from skylines.config import environment
from skylines.model import Competition


# Parse command line parameters

parser = argparse.ArgumentParser(
    description='List all competitions.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

args = parser.parse_args()

# Load environment

if not environment.load_from_file(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

# List participants of the competition

query = Competition.query() \
    .order_by(Competition.start_date.desc(), Competition.end_date.desc())


def print_competition(competition):
    output = '{} (id: {}), start: {}, end: {}'.format(
        competition.name.encode('utf8'), competition.id,
        competition.start_date, competition.end_date)

    print output

map(print_competition, query)
