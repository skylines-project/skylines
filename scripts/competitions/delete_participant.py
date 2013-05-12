#!/usr/bin/env python
#
# Deletes a participant from a competition
#

import argparse
from datetime import datetime
import transaction

from skylines.config import environment
from skylines.model.session import DBSession
from skylines.model import CompetitionParticipation


# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Deletes a participant from a competition.')

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

# Delete the participation from the competition

num = CompetitionParticipation.query(
    competition_id=args.competition_id, user_id=args.participant_id).delete()

if num:
    print 'Participant with id: {} got deleted from competition with id: {}.' \
        .format(args.participant_id, args.competition_id)
else:
    print 'No participant with id: {} found in competition with id: {}.' \
        .format(args.participant_id, args.competition_id)

transaction.commit()
