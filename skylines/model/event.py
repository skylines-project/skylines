from datetime import datetime
from itertools import chain

from sqlalchemy.types import Integer, DateTime

from skylines.database import db
from .user import User
from .club import Club
from .follower import Follower
from .flight import Flight


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


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    # The event of this notification

    event_id = db.Column(
        Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    event = db.relationship('Event', innerjoin=True)

    # The recipient of this notification

    recipient_id = db.Column(
        Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient = db.relationship('User', innerjoin=True)

    # The time that this notification was read by the recipient

    time_read = db.Column(DateTime)

    ##############################

    def __repr__(self):
        return '<Notification: id={}>' \
            .format(self.id).encode('unicode_escape')

    ##############################

    @classmethod
    def query_unread(cls, recipient):
        return cls.query(recipient=recipient, time_read=None) \
                  .join(cls.event) \
                  .outerjoin(Event.flight) \
                  .filter(Flight.is_rankable())

    @classmethod
    def count_unread(cls, recipient):
        return cls.query_unread(recipient).count()

    ##############################

    def mark_read(self):
        self.time_read = datetime.utcnow()

    @classmethod
    def mark_all_read(cls, recipient, filter_func=None):
        query = cls.query(recipient=recipient) \
            .outerjoin(Event) \
            .filter(Event.id == Notification.event_id)

        if filter_func is not None:
            query = filter_func(query)

        query.update(dict(time_read=datetime.utcnow()))


GROUPABLE_EVENT_TYPES = [
    Event.Type.FLIGHT,
    Event.Type.FOLLOWER,
]


class EventGroup:
    grouped = True

    def __init__(self, subevents, link=None):
        self.subevents = subevents

    @property
    def unread(self):
        """
        If this is a notification:
        `unread` is only false if all subnotifications are read.
        """

        for event in self.subevents:
            if hasattr(event, 'unread') and event.unread:
                return True

        return False

    def __getattr__(self, name):
        return getattr(self.subevents[0], name)


def create_flight_comment_notifications(comment):
    """
    Create notifications for the owner and pilots of the flight
    """

    flight = comment.flight
    user = comment.user

    # Create the event
    event = Event(type=Event.Type.FLIGHT_COMMENT,
                  actor=user, flight=flight, flight_comment=comment)

    db.session.add(event)

    # Create set of potential recipients
    recipients = {flight.igc_file.owner, flight.pilot, flight.co_pilot}
    recipients.discard(None)
    recipients.discard(user)

    # Create notifications for the recipients in the set
    for recipient in recipients:
        item = Notification(event=event, recipient=recipient)
        db.session.add(item)


def create_flight_notifications(flight):
    """
    Create notifications for the followers of the owner and pilots of the flight
    """

    # Create the event
    event = Event(type=Event.Type.FLIGHT,
                  actor_id=flight.igc_file.owner.id,
                  flight=flight)

    db.session.add(event)

    # Create list of flight-related users
    senders = {flight.pilot_id, flight.co_pilot_id, flight.igc_file.owner.id}
    senders.discard(None)

    # Request followers/recipients of the flight-related users from the DB
    followers = db.session.query(Follower.source_id.label('id')) \
                          .filter(Follower.destination_id.in_(senders))

    # Determine the recipients
    recipients = set([follower.id for follower in followers])

    # Don't send notifications to the senders if they follow each other
    recipients.difference_update(senders)

    # Create notifications for the recipients
    for recipient in recipients:
        item = Notification(event=event, recipient_id=recipient)
        db.session.add(item)


def create_follower_notification(followed, follower):
    """
    Create notification for the followed pilot about his new follower
    """

    # Create the event
    event = Event(type=Event.Type.FOLLOWER, actor=follower, user=followed)
    db.session.add(event)

    # Create the notification
    item = Notification(event=event, recipient=followed)
    db.session.add(item)


def create_new_user_event(user):
    """
    Create event for a new SkyLines user.
    """

    # Create the event
    event = Event(type=Event.Type.NEW_USER, actor=user)
    db.session.add(event)


def create_club_join_event(club, user):
    """
    Create event for a user joining a club.
    """

    if club is None:
        return

    if isinstance(club, Club):
        club = club.id

    # Create the event
    event = Event(type=Event.Type.CLUB_JOIN, actor=user, club_id=club)
    db.session.add(event)

    # Create the notifications for club members and followers
    q1 = db.session.query(User.id).filter_by(club_id=club)
    q2 = db.session.query(Follower.source_id).filter_by(destination_id=user.id)

    recipients = set([row[0] for row in chain(q1, q2)])
    for recipient in recipients:
        item = Notification(event=event, recipient_id=recipient)
        db.session.add(item)


def group_events(_events):
    events = []
    for event in _events:
        # add first event if list is empty
        if not events:
            events.append(event)
            continue

        # get last event from list for comparison
        last_event = events[-1]

        # if there are multiple groupable events from the same actor -> group them
        if (event.type in GROUPABLE_EVENT_TYPES and
                last_event.type == event.type and
                last_event.actor_id == event.actor_id):
            if isinstance(last_event, EventGroup):
                last_event.subevents.append(event)
            else:
                events[-1] = EventGroup([last_event, event])
            continue

        events.append(event)

    return events
