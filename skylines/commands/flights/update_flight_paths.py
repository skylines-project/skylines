from flask.ext.script import Command, Option

from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import or_
from skylines.model import db, Flight


class UpdateFlightPaths(Command):
    """ Update Skylines flight paths """

    option_list = (
        Option('--force', action='store_true',
               help='re-analyse all flights, not just the scheduled ones'),
        Option('ids', metavar='ID', nargs='*', type=int,
               help='Any number of flight IDs.'),
    )

    def run(self, force, ids):
        q = db.session.query(Flight)
        q = q.options(joinedload(Flight.igc_file))
        if ids:
            self.apply_and_commit(self.do, q.filter(Flight.id.in_(ids)))
        elif force:
            self.incremental(self.do, q)
        else:
            self.incremental(self.do, q.filter(
                or_(Flight.locations == None, Flight.timestamps == None)))

    def do(self, flight):
        print flight.id
        return flight.update_flight_path()

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
