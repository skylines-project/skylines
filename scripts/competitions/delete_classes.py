#!/usr/bin/env python
#
# Deletes a participant from a competition
#

import argparse
import transaction

from skylines.config import environment
from skylines.model import CompetitionClass


# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Deletes a participant from a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(metavar='competition-id', dest='competition_id', type=int,
                    help='id of the competition')
parser.add_argument(metavar='class-id', dest='class_ids', type=int, nargs='+',
                    help='id of the competition class')

args = parser.parse_args()

# Load environment

if not environment.load_from_file(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

# Delete the competition class from the competition

for class_id in args.class_ids:
    num = query = CompetitionClass.query(
        id=class_id, competition_id=args.competition_id).delete()

    if num:
        print 'Competition class with id: {} got deleted from competition with id: {}.' \
            .format(class_id, args.competition_id)
    else:
        print 'No competition class with id: {} found in competition with id: {}.' \
            .format(class_id, args.competition_id)

transaction.commit()
