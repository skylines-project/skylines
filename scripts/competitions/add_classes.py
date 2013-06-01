#!/usr/bin/env python
#
# Add a new competition class to a competition
#

import argparse
from config import to_envvar

# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Add a new competition class to a competition.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument(
    'competition_id', type=int, help='id of the competition')
parser.add_argument(metavar='class-name', dest='class_names', nargs='+',
                    help='name of the competition class')

args = parser.parse_args()

# Load environment

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from datetime import datetime
from skylines.model.session import DBSession
from skylines.model import CompetitionClass

# Add the competition classes to the competition

for class_name in args.class_names:

    class_ = CompetitionClass(
        competition_id=args.competition_id,
        name=class_name
    )

    DBSession.add(class_)
    DBSession.flush()

    print 'Competition class "{}" created with id: {}' \
        .format(class_.name, class_.id)

DBSession.commit()
