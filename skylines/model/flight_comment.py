from datetime import datetime
from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import relation, backref
from sqlalchemy.types import Unicode, Integer, DateTime
from skylines.model.base import DeclarativeBase
from skylines.model.auth import User
from skylines.model.flight import Flight


class FlightComment(DeclarativeBase):
    __tablename__ = 'flight_comments'

    id = Column(Integer, autoincrement=True, primary_key=True)

    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    flight_id = Column(Integer, ForeignKey('flights.id', ondelete='CASCADE'),
                       nullable=False, index=True)
    flight = relation('Flight', primaryjoin=(flight_id == Flight.id),
                      backref=backref('comments',
                                      order_by=time_created,
                                      cascade='all,delete-orphan',
                                      passive_deletes=True))

    user_id = Column(Integer, ForeignKey('tg_user.id', ondelete='SET NULL'))
    user = relation('User', primaryjoin=(user_id == User.id))

    text = Column(Unicode, nullable=False)
