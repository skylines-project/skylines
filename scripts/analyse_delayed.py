#!/usr/bin/env python
#
# Schedule flight reanalysis via celery worker.
#

import argparse
from config import to_envvar

parser = argparse.ArgumentParser(description='Re-analyse Skylines flights.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('--force', action='store_true',
                    help='re-analyse all flights, not just the scheduled ones')
parser.add_argument('ids', metavar='ID', nargs='*', type=int,
                    help='Any number of flight IDs.')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from skylines.model import Flight
from skylines.worker import tasks


def do(flight_id):
    print flight_id
    tasks.analyse_flight.delay(flight_id)


if args.force:
    # invalidate all results
    Flight.query().update({'needs_analysis': True})

if args.ids:
    for flight_id in args.ids:
        do(flight_id)
else:
    for flight in Flight.query(needs_analysis=True):
        do(flight.id)
