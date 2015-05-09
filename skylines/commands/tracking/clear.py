from flask.ext.script import Command, Option
from skylines.database import db
from skylines.model import TrackingFix


class Clear(Command):
    """ Clear all live tracks for a certain user """

    option_list = (
        Option('user', type=int, help='a user ID'),
    )

    def run(self, user):
        result = TrackingFix.query(pilot_id=user).delete()
        db.session.commit()

        print '%d live tracks cleared.' % result
