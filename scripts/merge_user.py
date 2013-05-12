#!/usr/bin/env python
#
# Merge two User records.
#

import sys
import os
import argparse
import transaction
from skylines.config import environment
from skylines.model import *

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Merge two SkyLines user accounts.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('new_id', type=int, help='ID of the new user account')
parser.add_argument('old_id', type=int, help='ID of the old user account')

args = parser.parse_args()

if not environment.load_from_file(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))

new_id = args.new_id
new = DBSession.query(User).get(new_id)
if not new:
    print >>sys.stderr, "No such user: %d" % new_id

old_id = args.old_id
old = DBSession.query(User).get(old_id)
if not old:
    print >>sys.stderr, "No such user: %d" % old_id

if old.club != new.club:
    print >>sys.stderr, "Different club;", old.club, new.club
    sys.exit(1)

DBSession.query(Club).filter_by(owner_id=old_id).update({'owner_id': new_id})
DBSession.query(IGCFile).filter_by(owner_id=old_id).update({'owner_id': new_id})
DBSession.query(Flight).filter_by(pilot_id=old_id).update({'pilot_id': new_id})
DBSession.query(Flight).filter_by(co_pilot_id=old_id).update({'co_pilot_id': new_id})
DBSession.query(TrackingFix).filter_by(pilot_id=old_id).update({'pilot_id': new_id})
DBSession.flush()
transaction.commit()

new = DBSession.query(User).get(new_id)
old = DBSession.query(User).get(old_id)
assert new and old

DBSession.delete(old)
DBSession.flush()

if new.user_name == new.name:
    new.user_name = old.user_name

if new.email_address is None and old.email_address is not None:
    new.email_address = old.email_address

if new._password is None and old._password is not None:
    new._password = old._password

# TODO: merge display name or not?
# TODO: merge tracking key or not?

DBSession.flush()
transaction.commit()
