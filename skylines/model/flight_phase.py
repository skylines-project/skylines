from sqlalchemy.types import Boolean, Float, Integer, DateTime, Interval

from skylines.database import db


class FlightPhase(db.Model):
    __tablename__ = 'flight_phases'

    # Flight phase types
    PT_POWERED = 1
    PT_CRUISE = 2
    PT_CIRCLING = 3

    # Circling directions
    CD_LEFT = 1
    CD_MIXED = 2
    CD_RIGHT = 3
    CD_TOTAL = 4

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    flight_id = db.Column(Integer, db.ForeignKey('flights.id', ondelete='CASCADE'),
                          nullable=False, index=True)

    start_time = db.Column(DateTime)
    end_time = db.Column(DateTime)

    flight = db.relationship(
        'Flight', innerjoin=True,
        backref=db.backref('_phases', passive_deletes=True, order_by=start_time,
                           cascade='all, delete, delete-orphan'))

    aggregate = db.Column(Boolean, nullable=False)
    phase_type = db.Column(Integer)  # see PT_* constants
    circling_direction = db.Column(Integer)  # see CD_* constants
    alt_diff = db.Column(Integer)
    duration = db.Column(Interval)
    fraction = db.Column(Integer)
    distance = db.Column(Integer)
    speed = db.Column(Float)
    vario = db.Column(Float)
    glide_rate = db.Column(Float)
    count = db.Column(Integer, nullable=False)
