from flask.ext.script import Command, Option

from flask import current_app
from sqlalchemy.orm import joinedload
from skylines.database import db
from skylines.model import Flight
from skylines.lib.xcsoar_ import analyse_flight
from skylines.worker import tasks

from selector import selector_options, select


class Analyze(Command):
    """ (Re)analyze flights """

    option_list = selector_options + (
        Option('--force', action='store_true',
               help='re-analyse all flights, not just the scheduled ones'),
    )

    def run(self, force, **kwargs):
        q = db.session.query(Flight)
        q = q.options(joinedload(Flight.igc_file))
        q = q.order_by(Flight.id)

        q = select(q, **kwargs)

        if not q:
            quit()

        if not force:
            q = q.filter(Flight.needs_analysis == True)

        self.incremental(self.do, q)

    def do(self, flight):
        print flight.id
        return analyse_flight(flight)

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
            offset += n_success + n_failed


class AnalyzeDelayed(Command):
    """ Schedule flight reanalysis via celery worker """

    option_list = selector_options + (
        Option('--force', action='store_true',
               help='re-analyse all flights, not just the scheduled ones'),
    )

    def run(self, force, **kwargs):
        current_app.add_celery()

        q = db.session.query(Flight)
        q = q.options(joinedload(Flight.igc_file))
        q = q.order_by(Flight.id)

        q = select(q, **kwargs)

        if not q:
            quit()

        if not force:
            q = q.filter(Flight.needs_analysis == True)

        for flight in q:
            self.do(flight.id)

    def do(self, flight_id):
        print flight_id
        tasks.analyse_flight.delay(flight_id)
