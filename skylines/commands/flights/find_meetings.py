from flask.ext.script import Command, Option
from sqlalchemy.sql.expression import and_, or_
from skylines.model import db, Flight, FlightPathChunks, FlightMeetings


class FindMeetings(Command):
    """ Find meetings points between flights """

    option_list = (
        Option('--force', action='store_true',
               help='re-analyse all flights, not just the scheduled ones'),
        Option('ids', metavar='ID', nargs='*', type=int,
               help='Any number of flight IDs.'),
    )

    def run(self, force, ids):
        q = db.session.query(Flight)
        q = q.order_by(Flight.id)

        if ids:
            self.apply_and_commit(self.do, q.filter(Flight.id.in_(ids)))
        elif force:
            self.incremental(self.do, q)

    def do(self, flight):
        print flight.id
        other_flights = FlightPathChunks.get_near_flights(flight)

        # delete all previous detected points between src and dst
        for key in other_flights:
            FlightMeetings.query() \
                .filter(or_(and_(FlightMeetings.source == flight, FlightMeetings.destination_id == key),
                            and_(FlightMeetings.destination == flight, FlightMeetings.source_id == key))) \
                .delete()

        # Insert new meetings into table
        for key, value in other_flights.iteritems():
            other_flight = Flight.get(key)

            FlightMeetings.add_meeting(flight, other_flight, value['times'][0], value['times'][-1])

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
