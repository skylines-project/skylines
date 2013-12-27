from flask.ext.script import Command
from skylines.model import db, User


class FillMissingKeys(Command):
    """ Generate tracking keys for user accounts that don't have one. """

    def run(self):
        keyless_users = User.query(tracking_key=None)

        for i, user in enumerate(keyless_users):
            user.generate_tracking_key()

            if i % 25 == 0:
                db.session.flush()

        db.session.commit()
