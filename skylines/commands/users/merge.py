from flask.ext.script import Command, Option

import sys

from skylines.database import db
from skylines.model import User, Club, IGCFile, Flight, TrackingFix


class Merge(Command):
    """ Merge two user accounts """

    option_list = (
        Option('new_id', type=int, help='ID of the new user account'),
        Option('old_id', type=int, help='ID of the old user account'),
    )

    def run(self, new_id, old_id):
        new = db.session.query(User).get(new_id)
        if not new:
            print >>sys.stderr, "No such user: %d" % new_id

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

        if new.email_address is None and old.email_address is not None:
            new.email_address = old.email_address

        if new._password is None and old._password is not None:
            new._password = old._password

        # TODO: merge display name or not?

        if old.tracking_key is not None:
            new.tracking_key = old.tracking_key

        db.session.commit()
