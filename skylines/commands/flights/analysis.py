from flask.ext.script import Command, Option

from flask import current_app
from sqlalchemy.orm import joinedload
from skylines.model import db, Flight
from skylines.lib.xcsoar_ import analyse_flight
from skylines.worker import tasks


class Analyze(Command):
    """ (Re)analyze flights """

    option_list = (
        Option('--force', action='store_true',
               help='re-analyse all flights, not just the scheduled ones'),
        Option('ids', metavar='ID', nargs='*', type=int,
               help='Any number of flight IDs.'),
    )

    def run(self, force, ids):
        if force:
            # invalidate all results
            db.session.query(Flight).update({'needs_analysis': True})

        q = db.session.query(Flight)
        q = q.options(joinedload(Flight.igc_file))
        if ids:
            self.apply_and_commit(self.do, q.filter(Flight.id.in_(ids)))
        else:
            self.incremental(self.do, q.filter(Flight.needs_analysis == True))

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
            offset += n_failed


class AnalyzeDelayed(Command):
    """ Schedule flight reanalysis via celery worker """

    option_list = (
        Option('--force', action='store_true',
               help='re-analyse all flights, not just the scheduled ones'),
        Option('ids', metavar='ID', nargs='*', type=int,
               help='Any number of flight IDs.'),
    )

    def run(self, force, ids):
        current_app.add_celery()

        if force:
            # invalidate all results
            Flight.query().update({'needs_analysis': True})

        if ids:
            for flight_id in ids:
                self.do(flight_id)
        else:
            for flight in Flight.query(needs_analysis=True):
                self.do(flight.id)

    def do(self, flight_id):
        print flight_id
        tasks.analyse_flight.delay(flight_id)
