#!/usr/bin/env python
#
# Merge two User records.
#

import sys
import os
import argparse
from config import to_envvar

sys.path.append(os.path.dirname(sys.argv[0]))

parser = argparse.ArgumentParser(description='Merge two SkyLines user accounts.')
parser.add_argument('--config', metavar='config.ini',
                    help='path to the configuration INI file')
parser.add_argument('new_id', type=int, help='ID of the new user account')
parser.add_argument('old_id', type=int, help='ID of the old user account')

args = parser.parse_args()

if not to_envvar(args.config):
    parser.error('Config file "{}" not found.'.format(args.config))


from skylines import db
from skylines.model import *


new_id = args.new_id
new = db.session.query(User).get(new_id)
if not new:
    print >>sys.stderr, "No such user: %d" % new_id

old_id = args.old_id
old = db.session.query(User).get(old_id)
if not old:
    print >>sys.stderr, "No such user: %d" % old_id

if old.club != new.club:
    print >>sys.stderr, "Different club;", old.club, new.club
    sys.exit(1)

db.session.query(Club).filter_by(owner_id=old_id).update({'owner_id': new_id})
db.session.query(IGCFile).filter_by(owner_id=old_id).update({'owner_id': new_id})
db.session.query(Flight).filter_by(pilot_id=old_id).update({'pilot_id': new_id})
db.session.query(Flight).filter_by(co_pilot_id=old_id).update({'co_pilot_id': new_id})
db.session.query(TrackingFix).filter_by(pilot_id=old_id).update({'pilot_id': new_id})
db.session.flush()
db.session.commit()

new = db.session.query(User).get(new_id)
old = db.session.query(User).get(old_id)
assert new and old

db.session.delete(old)
db.session.flush()

if new.user_name == new.name:
    new.user_name = old.user_name

if new.email_address is None and old.email_address is not None:
    new.email_address = old.email_address

if new._password is None and old._password is not None:
    new._password = old._password

# TODO: merge display name or not?
# TODO: merge tracking key or not?

db.session.commit()
