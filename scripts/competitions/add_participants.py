#!/usr/bin/env python
#
# Add a new participant to a competition
#

import argparse
from config import to_envvar

# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Add a new participant to a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    'competition_id', type=int, help='id of the competition')

parser.add_argument(metavar='participant-id', dest='participant_ids',
                    nargs='+', type=int, help='id of the participant')

parser.add_argument('--class', dest='class_id', type=int,
                    help='id of the competition class')

args = parser.parse_args()

# Load environment

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


import sys
from datetime import datetime

from skylines.model.session import DBSession
from skylines.model import CompetitionParticipation, CompetitionClass

# Add the participants to the competition

for participant_id in args.participant_ids:

    participation = CompetitionParticipation(
        competition_id=args.competition_id,
        user_id=participant_id,
        join_time=datetime.utcnow())

    if args.class_id:
        participation.class_ = CompetitionClass.get(args.class_id)
        if not participation.class_:
            sys.exit('There is no competition class with id: {} in competition with id: {}'
                     .format(args.class_id, args.competition_id))

    DBSession.add(participation)
    DBSession.flush()

    print 'Participation object created with id: {}' \
        .format(participation.id)

DBSession.commit()
