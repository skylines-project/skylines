#!/usr/bin/env python
#
# List all participants of a competition
#

import sys
import argparse

from sqlalchemy.orm import contains_eager

from skylines.config import environment
from skylines.model import Competition, CompetitionParticipation


# Parse command line parameters

parser = argparse.ArgumentParser(
    description='List all participants of a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    'competition_id', type=int, help='id of the competition')

args = parser.parse_args()

# Load environment

if not environment.load_from_file(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

# List participants of the competition

competition = Competition.get(args.competition_id)
if not competition:
    sys.exit('No competition found with id: {}.'.format(args.competition_id))

query = CompetitionParticipation.query(competition=competition) \
    .join('user').options(contains_eager('user'))

query = query.order_by('tg_user.name')


def print_participant(participant):
    output = '{} (id: {})'.format(
        participant.user.name.encode('utf8'), participant.user_id)

    if participant.class_id:
        output = output + ' (class: {})'.format(participant.class_id)

    print output

map(print_participant, query)
