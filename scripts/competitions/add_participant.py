#!/usr/bin/env python
#
# Add a new participant to a competition
#

import argparse
from datetime import datetime
import transaction

from skylines.config import environment
from skylines.model.session import DBSession
from skylines.model import CompetitionParticipation


# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Add a new competition to the database.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    'competition_id', type=int, help='id of the competition')
parser.add_argument(
    'participant_id', type=int, help='id of the participant')

args = parser.parse_args()

# Load environment

if not environment.load_from_file(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

# Add the participant to the competition

participation = CompetitionParticipation(
    competition_id=args.competition_id,
    user_id=args.participant_id,
    pilot_time=datetime.utcnow()
)

DBSession.add(participation)
DBSession.flush()

print 'Participation object created with id: {}' \
    .format(participation.id)

transaction.commit()
