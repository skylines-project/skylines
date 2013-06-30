#!/usr/bin/env python
#
# Copy igc files by some criteria to a destination directory
#

import sys
import os
import argparse
from config import to_envvar
import shutil

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Copy flight files by one or more properties.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('--flight_id', type=int, help='ID of the flight')
parser.add_argument('--country_code', help='Country code of the start airport')
parser.add_argument('--airport_name', help='Airport name of the start airport')
parser.add_argument('--date_from', help='Date from (YYYY-MM-DD)')
parser.add_argument('--date_to', help='Date to (YYYY-MM-DD)')
parser.add_argument('--dest', help='Destination directory')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

if not os.path.exists(args.dest):
    print "Please create destination directory: " + args.dest
    quit()

dest_dir = args.dest

from skylines import app, db
from skylines.model import Airport, Flight, IGCFile
from sqlalchemy import func
from time import mktime, strptime
from datetime import datetime

query = db.session.query(Flight).join(Flight.takeoff_airport).join(IGCFile)

if args.flight_id is not None:
    print "Filter by flight id: " + str(args.flight_id)
    query = query.filter(Flight.id == args.flight_id)

if args.country_code is not None:
    print "Filter by takeoff airport country code: " + str(args.country_code)
    query = query.filter(func.lower(Airport.country_code) == func.lower(str(args.country_code)))

if args.airport_name is not None:
    print "Filter by takeoff airport name: " + str(args.airport_name)
    query = query.filter(func.lower(Airport.name) == func.lower(str(args.airport_name)))

if args.date_from is not None:
    try:
        date_from = strptime(args.date_from, "%Y-%m-%d")
    except:
        print "Cannot parse from date."
        quit()

    query = query.filter(Flight.takeoff_time >= datetime.fromtimestamp(mktime(date_from)))

if args.date_to is not None:
    try:
        date_to = strptime(args.date_to, "%Y-%m-%d")
    except:
        print "Cannot parse to date."
        quit()

    query = query.filter(Flight.takeoff_time <= datetime.fromtimestamp(mktime(date_to)))


for flight in query:
    print "Flight: " + str(flight.id) + " " + flight.igc_file.filename
    shutil.copy(os.path.join(app.config['SKYLINES_FILES_PATH'], flight.igc_file.filename), dest_dir)
