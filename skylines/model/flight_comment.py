from datetime import datetime

from sqlalchemy.types import Unicode, Integer, DateTime

from skylines.database import db


class FlightComment(db.Model):
    __tablename__ = 'flight_comments'

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    flight_id = db.Column(Integer, db.ForeignKey('flights.id', ondelete='CASCADE'),
                          nullable=False, index=True)
    flight = db.relationship(
        'Flight', innerjoin=True,
        backref=db.backref('comments', order_by=time_created,
                           passive_deletes=True))

    user_id = db.Column(Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    user = db.relationship('User', lazy='joined')

    def __repr__(self):
        return ('<FlightComment: id=%d user_id=%d flight_id=%d>' % (self.id, self.user_id, self.flight_id)).encode('unicode_escape')

    text = db.Column(Unicode, nullable=False)
