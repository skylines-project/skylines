from __future__ import print_function

from datetime import datetime, timedelta

from flask_script import Command
from skylines.database import db
from skylines.model import TrackingFix


class DeleteOld(Command):
    """ Clear old live tracks """

    def run(self):
        max_age = timedelta(weeks=2)

        result = (
            db.session.query(TrackingFix)
            .filter(TrackingFix.time < datetime.utcnow() - max_age)
            .delete()
        )

        db.session.commit()

        print("%d live tracking locations cleared." % result)
