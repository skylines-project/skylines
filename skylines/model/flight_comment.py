from datetime import datetime

from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Unicode, Integer, DateTime

from skylines import db


class FlightComment(db.Model):
    __tablename__ = 'flight_comments'

    id = Column(Integer, autoincrement=True, primary_key=True)

    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    flight_id = Column(Integer, ForeignKey('flights.id', ondelete='CASCADE'),
                       nullable=False, index=True)
    flight = relationship(
        'Flight', innerjoin=True,
        backref=backref('comments', order_by=time_created,
                        passive_deletes=True))

    user_id = Column(Integer, ForeignKey('tg_user.id', ondelete='SET NULL'))
    user = relationship('User')

    def __repr__(self):
        return ('<FlightComment: id=%d user_id=%d flight_id=%d>' % (self.id, self.user_id, self.flight_id)).encode('utf-8')

    text = Column(Unicode, nullable=False)
