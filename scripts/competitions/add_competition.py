#!/usr/bin/env python
#
# Add a new competition
#

import argparse
import transaction

from formencode.validators import DateConverter

from skylines.config import environment
from skylines.model.session import DBSession
from skylines.model import Competition


# Parse command line parameters

parser = argparse.ArgumentParser(
    description='Add a new competition to the database.')

parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')

parser.add_argument('name', help='name of the competition')
parser.add_argument('start', help='start date (dd.mm.yyyy)')
parser.add_argument('end', help='end date (dd.mm.yyyy)')
parser.add_argument('--creator', type=int, help='id of the creator')

args = parser.parse_args()

# Load environment

if not environment.load_from_file(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


# Parse start date

date_converter = DateConverter(month_style='dd/mm/yyyy')

try:
    args.start = date_converter.to_python(args.start)
except:
    parser.error('"{}" is not a valid date'.format(args.start))

# Parse end date

try:
    args.end = date_converter.to_python(args.end)
except:
    parser.error('"{}" is not a valid date'.format(args.end))

# Check dates

if args.start > args.end:
    parser.error('The start date has to be before the end date.')

# Create competition

competition = Competition(
    name=args.name, start_date=args.start, end_date=args.end)

if args.creator:
    competition.creator_id = args.creator

DBSession.add(competition)
DBSession.flush()

print 'Competition "{}" created with id: {}' \
    .format(competition.name, competition.id)

transaction.commit()
