from collections import OrderedDict

from sqlalchemy.types import Integer, DateTime
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import aliased

from skylines.database import db
from skylines.model import Flight


class FlightMeetings(db.Model):
    __tablename__ = 'flight_meetings'

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    source_id = db.Column(
        Integer, db.ForeignKey('flights.id', ondelete='CASCADE'),
        index=True, nullable=False)
    source = db.relationship(
        'Flight', foreign_keys=[source_id])

    destination_id = db.Column(
        Integer, db.ForeignKey('flights.id', ondelete='CASCADE'),
        index=True, nullable=False)
    destination = db.relationship(
        'Flight', foreign_keys=[destination_id])

    start_time = db.Column(DateTime, nullable=False)
    end_time = db.Column(DateTime, nullable=False)

    @classmethod
    def get_meetings(cls, source):
        flight_source = aliased(Flight, name='flight_source')
        flight_destination = aliased(Flight, name='flight_destination')

        q = cls.query() \
               .filter(or_(cls.source == source, cls.destination == source)) \
               .join(flight_source, cls.source_id == flight_source.id) \
               .join(flight_destination, cls.destination_id == flight_destination.id) \
               .filter(flight_source.is_rankable()) \
               .filter(flight_destination.is_rankable()) \
               .order_by(cls.start_time)

        meetings = OrderedDict()
        for mp in q:
            flight = mp.source if mp.source != source else mp.destination

            if flight.id not in meetings:
                meetings[flight.id] = dict(
                    flight=flight,
                    times=[]
                )

            meetings[flight.id]['times'].append(dict(
                start=mp.start_time,
                end=mp.end_time
            ))

        return meetings

    @classmethod
    def add_meeting(cls, source, destination, start_time, end_time):
        if source == destination:
            return

        mp = FlightMeetings(source=source, destination=destination,
                            start_time=start_time, end_time=end_time)

        db.session.add(mp)
