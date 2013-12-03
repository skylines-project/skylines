#!/usr/bin/env python

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Update Skylines flight paths.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('--force', action='store_true',
                    help='update all flights, not just the scheduled ones')
parser.add_argument('ids', metavar='ID', nargs='*', type=int,
                    help='Any number of flight IDs.')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
from skylines import app
from skylines.model import db, Flight

app.app_context().push()


def do(flight):
    print flight.id
    return flight.update_flight_path()


def apply_and_commit(func, q):
    n_success, n_failed = 0, 0
    for record in q:
        if func(record):
            n_success += 1
        else:
            n_failed += 1
    if n_success > 0:
        print "commit"
        db.session.commit()
    return n_success, n_failed


def incremental(func, q):
    """Repeatedly query 10 records and invoke the callback, commit
    after each chunk."""
    n = 10
    offset = 0
    while True:
        n_success, n_failed = apply_and_commit(func, q.offset(offset).limit(n))
        if n_success == 0 and n_failed == 0:
            break
        offset += n_failed

q = db.session.query(Flight)
q = q.options(joinedload(Flight.igc_file))
if args.ids:
    apply_and_commit(do, q.filter(Flight.id.in_(args.ids)))
elif args.force:
    incremental(do, q)
else:
    incremental(do, q.filter(or_(Flight.locations == None,
                                 Flight.timestamps == None)))
