#!/usr/bin/env python
#
# Deletes a competition
#

import argparse
import transaction

from skylines.config import environment
from skylines.model.session import DBSession
from skylines.model import Competition


# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Deletes a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    'competition_id', type=int, help='id of the competition')

args = parser.parse_args()

# Load environment

if not environment.load_from_file(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

# Delete the competition

num = Competition.query(id=args.competition_id).delete()

if num:
    print 'Competition with id: {} got deleted.'.format(args.competition_id)
else:
    print 'No competition with id: {} found.'.format(args.competition_id)

transaction.commit()
