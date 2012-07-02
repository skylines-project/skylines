#!/usr/bin/python
#
# Merge two User records.
#

import sys, os
import transaction
from paste.deploy.loadwsgi import appconfig
from skylines.config.environment import load_environment
from skylines.model import *

sys.path.append(os.path.dirname(sys.argv[0]))

conf_path = '/etc/skylines/production.ini'
if len(sys.argv) > 3:
    conf_path = sys.argv[1]
    del sys.argv[1]

if len(sys.argv) != 3:
    print >>sys.stderr, "Usage: %s [config.ini] NEW_ID OLD_ID" % sys.argv[0]
    sys.exit(1)

conf = appconfig('config:' + os.path.abspath(conf_path))
load_environment(conf.global_conf, conf.local_conf)

new_id = int(sys.argv[1])
new = DBSession.query(User).get(new_id)
if not new:
    print >>sys.stderr, "No such user: %d" % new_id

old_id = int(sys.argv[2])
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

if new.user_name == new.display_name:
    new.user_name = old.user_name

if new.email_address is None and old.email_address is not None:
    new.email_address = old.email_address

if new._password is None and old._password is not None:
    new._password = old._password

# TODO: merge display name or not?
# TODO: merge tracking key or not?

DBSession.flush()
transaction.commit()
