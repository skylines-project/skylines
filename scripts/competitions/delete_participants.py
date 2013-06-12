#!/usr/bin/env python
#
# Deletes a participant from a competition
#

import argparse
from config import to_envvar

# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Deletes a participant from a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    metavar='competition-id', dest='competition_id', type=int,
    help='id of the competition')

parser.add_argument(
    metavar='participant-id', dest='participant_ids', nargs='*', type=int,
    help='id of the participant')

parser.add_argument('--all', action='store_true',
                    help='delete all participants of the competition')

args = parser.parse_args()

# Check --all or participant_ids are available

if not (bool(args.all) ^ bool(args.participant_ids)):
    parser.error('You have to use either --all or specify one or more participant ids.')

# Load environment

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from skylines import db
from skylines.model import CompetitionParticipation

# Delete all participants from the competition

if args.all:
    num = CompetitionParticipation.query(
        competition_id=args.competition_id).delete()

    if num:
        print '{} participants got deleted from competition with id: {}.' \
            .format(num, args.competition_id)
    else:
        print 'No participants found in competition with id: {}.' \
            .format(args.competition_id)

# .. or delete specific participants from the competition

elif args.participant_ids:
    for participant_id in args.participant_ids:
        num = CompetitionParticipation.query(
            competition_id=args.competition_id, user_id=participant_id).delete()

        if num:
            print 'Participant with id: {} got deleted from competition with id: {}.' \
                .format(participant_id, args.competition_id)
        else:
            print 'No participant with id: {} found in competition with id: {}.' \
                .format(participant_id, args.competition_id)

db.session.commit()
