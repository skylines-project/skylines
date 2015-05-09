from flask.ext.script import Command, Option
from flask import current_app
from skylines.database import db
from skylines.model import Flight
from skylines.worker import tasks

from selector import selector_options, select


class FindMeetings(Command):
    """ Find meetings points between flights """

    option_list = selector_options + (
        Option('--force', action='store_true',
               help='re-analyse all flights, not just the scheduled ones'),
        Option('--async', action='store_true',
               help='put flights in celery queue'),
    )

    def run(self, force, async, **kwargs):
        q = db.session.query(Flight)
        q = q.order_by(Flight.id)

        q = select(q, **kwargs)

        if not q:
            quit()

        if not force:
            q = q.filter(Flight.needs_analysis == True)

        if async:
            current_app.add_celery()

        self.incremental(lambda f: self.do(f, async=async), q)

    def do(self, flight, async):
        print flight.id

        if async:
            tasks.find_meetings.delay(flight.id)
        else:
            tasks.find_meetings(flight.id)

        return True

    def apply_and_commit(self, func, q):
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

    def incremental(self, func, q):
        """Repeatedly query 10 records and invoke the callback, commit
        after each chunk."""
        n = 10
        offset = 0
        while True:
            n_success, n_failed = self.apply_and_commit(
                func, q.offset(offset).limit(n))
            if n_success == 0 and n_failed == 0:
                break
            offset += n_failed + n_success
