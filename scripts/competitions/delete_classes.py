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

parser.add_argument(metavar='competition-id', dest='competition_id', type=int,
                    help='id of the competition')

parser.add_argument(metavar='class-id', dest='class_ids', type=int, nargs='*',
                    help='id of the competition class')

parser.add_argument('--all', action='store_true',
                    help='remove all competition classes of the competition')

args = parser.parse_args()

# Check --all or class_ids are available

if not (bool(args.all) ^ bool(args.class_ids)):
    parser.error('You have to use either --all or specify one or more competition class ids.')

# Load environment

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from skylines import db
from skylines.model import CompetitionClass

# Delete all competition classes from the competition

if args.all:
    num = CompetitionClass.query(competition_id=args.competition_id).delete()

    if num:
        print '{} competition classes got deleted from competition with id: {}.' \
            .format(num, args.competition_id)
    else:
        print 'No competition classes found in competition with id: {}.' \
            .format(args.competition_id)

# .. or delete specific competition classes from the competition

elif args.class_ids:
    for class_id in args.class_ids:
        num = CompetitionClass.query(
            id=class_id, competition_id=args.competition_id).delete()

        if num:
            print 'Competition class with id: {} got deleted from competition with id: {}.' \
                .format(class_id, args.competition_id)
        else:
            print 'No competition class with id: {} found in competition with id: {}.' \
                .format(class_id, args.competition_id)

db.session.commit()
