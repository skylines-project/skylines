from sqlalchemy.types import Integer, DateTime
from sqlalchemy.sql.expression import or_
from skylines.model import db


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
        q = cls.query() \
               .filter(or_(cls.source == source, cls.destination == source)) \
               .order_by(cls.start_time)

        meetings = []
        for mp in q:
            meetings.append(dict(
                flight=mp.source if mp.source != source else mp.destination,
                start_time=mp.start_time,
                end_time=mp.end_time))

        return meetings

    @classmethod
    def add_meeting(cls, source, destination, start_time, end_time):
        if source == destination:
            return

        mp = FlightMeetings(source=source, destination=destination,
                            start_time=start_time, end_time=end_time)

        db.session.add(mp)
