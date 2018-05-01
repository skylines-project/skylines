from datetime import datetime

from sqlalchemy.types import Integer, DateTime

from skylines.database import db


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    # Notification type

    type = db.Column(Integer, nullable=False)

    class Type:
        FLIGHT_COMMENT = 1
        FLIGHT = 2
        FOLLOWER = 3
        NEW_USER = 4
        CLUB_JOIN = 5

    # Event time

    time = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    # The user that caused the event

    actor_id = db.Column(
        Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    actor = db.relationship('User', foreign_keys=[actor_id], innerjoin=True)

    # A user if this event is about a user (e.g. actor following user)

    user_id = db.Column(
        Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User', foreign_keys=[user_id])

    # A club if this event is about a club (e.g. actor joining club)

    club_id = db.Column(
        Integer, db.ForeignKey('clubs.id', ondelete='CASCADE'))
    club = db.relationship('Club')

    # A flight if this event is about a flight

    flight_id = db.Column(
        Integer, db.ForeignKey('flights.id', ondelete='CASCADE'))
    flight = db.relationship('Flight')

    # A flight comment if this event is about a flight comment

    flight_comment_id = db.Column(
        Integer, db.ForeignKey('flight_comments.id', ondelete='CASCADE'))
    flight_comment = db.relationship('FlightComment')

    ##############################

    def __repr__(self):
        return '<Event: id={} type={}>' \
            .format(self.id, self.type).encode('unicode_escape')
