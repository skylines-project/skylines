#!/usr/bin/env python
#
# Deletes a competition
#

import argparse
from config import to_envvar

# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Deletes a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    'competition_id', type=int, help='id of the competition')

args = parser.parse_args()

# Load environment

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from skylines.model import DBSession, Competition

# Delete the competition

num = Competition.query(id=args.competition_id).delete()

if num:
    print 'Competition with id: {} got deleted.'.format(args.competition_id)
else:
    print 'No competition with id: {} found.'.format(args.competition_id)

DBSession.commit()
