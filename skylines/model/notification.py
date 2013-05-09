from datetime import datetime
from collections import OrderedDict

from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import relationship, contains_eager
from sqlalchemy.types import Integer, DateTime

from .base import DeclarativeBase
from .session import DBSession
from .auth import User
from .flight import Flight
from .flight_comment import FlightComment
from .follower import Follower


class Event(DeclarativeBase):
    __tablename__ = 'events'

    id = Column(Integer, autoincrement=True, primary_key=True)

    # Notification type

    type = Column(Integer, nullable=False)

    class Type:
        FLIGHT_COMMENT = 1
        FLIGHT = 2
        FOLLOWER = 3

    # Event time

    time = Column(DateTime, nullable=False, default=datetime.utcnow)

    # The user that caused the event

    actor_id = Column(
        Integer, ForeignKey('tg_user.id', ondelete='CASCADE'), nullable=False)
    actor = relationship('User', innerjoin=True)

    # A flight if this event is about a flight

    flight_id = Column(
        Integer, ForeignKey('flights.id', ondelete='CASCADE'))
    flight = relationship('Flight')

    # A flight comment if this event is about a flight comment

    flight_comment_id = Column(
        Integer, ForeignKey('flight_comments.id', ondelete='CASCADE'))
    flight_comment = relationship('FlightComment')

    ##############################

    def __repr__(self):
        return '<Event: id={} type={}>' \
            .format(self.id, self.type).encode('utf-8')


class Notification(DeclarativeBase):
    __tablename__ = 'notifications'

    id = Column(Integer, autoincrement=True, primary_key=True)

    # The event of this notification

    event_id = Column(
        Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    event = relationship('Event', innerjoin=True)

    # The recipient of this notification

    recipient_id = Column(
        Integer, ForeignKey('tg_user.id', ondelete='CASCADE'), nullable=False)
    recipient = relationship('User', innerjoin=True)

    # The time that this notification was read by the recipient

    time_read = Column(DateTime)

    ##############################

    def __repr__(self):
        return '<Notification: id={}>' \
            .format(self.id).encode('utf-8')

    ##############################

    @classmethod
    def query_unread(cls, user):
        return cls.query(recipient=user, time_read=None)

    @classmethod
    def count_unread(cls, user):
        return cls.query_unread(user).count()

    ##############################

    def mark_read(self):
        self.time_read = datetime.utcnow()

    @classmethod
    def mark_all_read(cls, user, filter_func=None):
        query = cls.query(recipient=user) \
            .outerjoin(Event) \
            .filter(Event.id == Notification.event_id)

        if filter_func is not None:
            query = filter_func(query)

        query.update(dict(time_read=datetime.utcnow()))


def create_flight_comment_notifications(comment):
    '''
    Create notifications for the owner and pilots of the flight
    '''

    # Create the event
    event = Event(type=Event.Type.FLIGHT_COMMENT,
                  actor=comment.user,
                  flight=comment.flight,
                  flight_comment=comment)

    DBSession.add(event)

    # Create list of potential recipients (using Set to avoid duplicates)
    recipients = {comment.flight.igc_file.owner,
                  comment.flight.pilot,
                  comment.flight.co_pilot}

    # Create notifications for the recipients in the set
    for recipient in recipients:
        # There is no need to notify the user that caused the notification
        if recipient is None or recipient == comment.user:
            continue

        item = Notification(event=event, recipient=recipient)
        DBSession.add(item)


def create_flight_notifications(flight):
    '''
    Create notifications for the followers of the owner and pilots of the flight
    '''

    # Create the event
    event = Event(type=Event.Type.FLIGHT,
                  actor_id=flight.igc_file.owner.id,
                  flight=flight)

    DBSession.add(event)

    # Create list of flight-related users
    senders = {flight.pilot_id, flight.co_pilot_id, flight.igc_file.owner.id}
    senders.discard(None)

    # Request followers/recipients of the flight-related users from the DB
    followers = DBSession.query(Follower.source_id.label('id')) \
                         .filter(Follower.destination_id.in_(senders))

    # Determine the recipients
    recipients = set([follower.id for follower in followers])

    # Don't send notifications to the senders if they follow each other
    recipients.difference_update(senders)

    # Create notifications for the recipients
    for recipient in recipients:
        item = Notification(event=event, recipient_id=recipient)
        DBSession.add(item)


def create_follower_notification(followed, follower):
    '''
    Create notification for the followed pilot about his new follower
    '''

    # Create the event
    event = Event(type=Event.Type.FOLLOWER, actor=follower)
    DBSession.add(event)

    # Create the notification
    item = Notification(event=event, recipient=followed)
    DBSession.add(item)
