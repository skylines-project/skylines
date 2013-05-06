from datetime import datetime
from collections import OrderedDict

from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, DateTime

from .base import DeclarativeBase
from .session import DBSession
from .auth import User
from .flight import Flight
from .flight_comment import FlightComment
from .follower import Follower


class Notification(DeclarativeBase):
    __tablename__ = 'notifications'

    id = Column(Integer, autoincrement=True, primary_key=True)

    # Notification type (NT_* constants)
    type = Column(Integer, nullable=False)

    NT_FLIGHT_COMMENT = 1
    NT_FLIGHT = 2
    NT_FOLLOWER = 3

    # Time stamps
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_read = Column(DateTime)

    # The user that caused the notification (if any)
    sender_id = Column(Integer,
                       ForeignKey('tg_user.id', ondelete='CASCADE'),
                       nullable=False)

    sender = relation('User', foreign_keys=[sender_id])

    # The recipient of this notification
    recipient_id = Column(Integer,
                          ForeignKey('tg_user.id', ondelete='CASCADE'),
                          nullable=False)

    recipient = relation('User', foreign_keys=[recipient_id])

    # A flight if this notification is about a flight
    flight_id = Column(Integer, ForeignKey('flights.id', ondelete='CASCADE'))
    flight = relation('Flight')

    # A flight comment if this notification is about a flight comment
    flight_comment_id = Column(Integer,
                               ForeignKey('flight_comments.id', ondelete='CASCADE'))
    flight_comment = relation('FlightComment')

    def __repr__(self):
        return ('<Notification: id=%d type=%d>' % (self.id, self.type)).encode('utf-8')

    def mark_read(self):
        self.time_read = datetime.utcnow()

    @classmethod
    def mark_all_read(cls, user, filter_func=None):
        query = cls.query(recipient=user)

        if filter_func is not None:
            query = filter_func(query)

        query.update(dict(time_read=datetime.utcnow()))

    @classmethod
    def constants(cls):
        return {
            member: getattr(cls, member)
            for member in dir(cls) if member.isupper()
        }


def count_unread_notifications(user):
    return Notification.query(recipient=user, time_read=None).count()


def create_flight_comment_notifications(comment):
    '''
    Create notifications for the owner and pilots of the flight
    '''

    # Create list of potential recipients (using set to avoid duplicates)
    recipients = set([comment.flight.igc_file.owner,
                      comment.flight.pilot,
                      comment.flight.co_pilot])

    # Create notifications for the recipients in the set
    for recipient in recipients:
        # There is no need to notify the user that caused the notification
        if recipient is None or recipient == comment.user:
            continue

        item = Notification(type=Notification.NT_FLIGHT_COMMENT,
                            sender=comment.user,
                            recipient=recipient,
                            flight=comment.flight,
                            flight_comment=comment)
        DBSession.add(item)


def create_flight_notifications(flight):
    '''
    Create notifications for the followers of the owner and pilots of the flight
    '''

    # Create list of flight-related users
    senders = [flight.pilot_id, flight.co_pilot_id, flight.igc_file.owner_id]
    senders = OrderedDict([(s, None) for s in senders if s is not None])

    # Request followers/recipients of the flight-related users from the DB
    followers = DBSession.query(Follower.source_id, Follower.destination_id) \
                         .filter(Follower.destination_id.in_(senders.keys())) \
                         .all()

    # Determine the recipients and their most important sender

    recipients = dict()

    # For each flight-related user in decreasing importance ..
    for sender in senders.keys():
        # For each of his followers
        for follower in followers:
            if follower.destination_id != sender:
                continue

            # Don't send notifications to the senders if they follow each other
            if follower.source_id in senders:
                continue

            # If the recipient/follower is not registered
            # yet by a more important sender
            if follower.source_id not in recipients:
                # Register the recipient with the sender's id
                recipients[follower.source_id] = sender

    # Create notifications for the recipients
    for recipient, sender in recipients.iteritems():
        item = Notification(type=Notification.NT_FLIGHT,
                            sender_id=sender,
                            recipient_id=recipient,
                            flight=flight)
        DBSession.add(item)


def create_follower_notification(followed, follower):
    '''
    Create notification for the followed pilot about his new follower
    '''

    item = Notification(type=Notification.NT_FOLLOWER,
                        sender=follower,
                        recipient=followed)
    DBSession.add(item)
