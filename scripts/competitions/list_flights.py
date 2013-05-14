#!/usr/bin/env python
#
# List all classes of a competition
#

import sys
import argparse

from sqlalchemy.orm import joinedload

from skylines.config import environment
from skylines.model import (
    DBSession, Competition, CompetitionParticipation, Flight
)


# Parse command line parameters

parser = argparse.ArgumentParser(
    description='List all classes of a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    'competition_id', type=int, help='id of the competition')

parser.add_argument('--class', dest='class_id', type=int,
                    help='id of the competition class')

args = parser.parse_args()

# Load environment

if not environment.load_from_file(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

# List participants of the competition

competition = Competition.get(args.competition_id)
if not competition:
    sys.exit('No competition found with id: {}.'.format(args.competition_id))

subq = DBSession.query(CompetitionParticipation.user_id) \
    .filter_by(competition=competition) \
    .filter(CompetitionParticipation.pilot_time != None)

if args.class_id:
    subq = subq.filter_by(class_id=args.class_id)

subq = subq.subquery()

query = Flight.query() \
    .filter(Flight.pilot_id.in_(subq)) \
    .filter(Flight.date_local >= competition.start_date) \
    .filter(Flight.date_local <= competition.end_date) \
    .options(joinedload('pilot')) \
    .order_by(Flight.date_local.desc(), Flight.olc_plus_score.desc())


def print_flight(flight):
    print '{} | {} | {} | {} | {}'.format(
        str(flight.id).rjust(6), str(flight.date_local),
        flight.pilot.name.ljust(30).encode('utf8'),
        str(flight.olc_plus_score).rjust(5) + ' pt',
        str(flight.olc_classic_distance / 1000).rjust(5) + ' km')

map(print_flight, query)
