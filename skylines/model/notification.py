from datetime import datetime
from itertools import chain

from sqlalchemy.types import Integer, DateTime

from skylines.database import db
from skylines.lib.string import unicode_to_str
from .event import Event
from .user import User
from .club import Club
from .follower import Follower
from .flight import Flight


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    # The event of this notification

    event_id = db.Column(
        Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    event = db.relationship("Event", innerjoin=True)

    # The recipient of this notification

    recipient_id = db.Column(
        Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    recipient = db.relationship("User", innerjoin=True)

    # The time that this notification was read by the recipient

    time_read = db.Column(DateTime)

    ##############################

    def __repr__(self):
        return unicode_to_str("<Notification: id={}>".format(self.id))

    ##############################

    @classmethod
    def query_unread(cls, recipient):
        return (
            cls.query(recipient=recipient, time_read=None)
            .join(cls.event)
            .outerjoin(Event.flight)
            .filter(Flight.is_rankable())
        )

    @classmethod
    def count_unread(cls, recipient):
        return cls.query_unread(recipient).count()

    ##############################

    def mark_read(self):
        self.time_read = datetime.utcnow()

    @classmethod
    def mark_all_read(cls, recipient, filter_func=None):
        query = cls.query(recipient=recipient).filter(Event.id == Notification.event_id)

        if filter_func is not None:
            query = filter_func(query)

        query.update(dict(time_read=datetime.utcnow()), synchronize_session=False)


def create_flight_comment_notifications(comment):
    """
    Create notifications for the owner and pilots of the flight
    """

    flight = comment.flight
    user = comment.user

    # Create the event
    event = Event.for_flight_comment(comment)
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
    event = Event.for_flight(flight)
    db.session.add(event)

    # Create list of flight-related users
    senders = {flight.pilot_id, flight.co_pilot_id, flight.igc_file.owner.id}
    senders.discard(None)

    # Request followers/recipients of the flight-related users from the DB
    followers = db.session.query(Follower.source_id.label("id")).filter(
        Follower.destination_id.in_(senders)
    )

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
    event = Event.for_follower(followed, follower)
    db.session.add(event)

    # Create the notification
    item = Notification(event=event, recipient=followed)
    db.session.add(item)


def create_new_user_event(user):
    """
    Create event for a new SkyLines user.
    """

    # Create the event
    event = Event.for_new_user(user)
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
    event = Event.for_club_join(club, user)
    db.session.add(event)

    # Create the notifications for club members and followers
    q1 = db.session.query(User.id).filter_by(club_id=club)
    q2 = db.session.query(Follower.source_id).filter_by(destination_id=user.id)

    recipients = set([row[0] for row in chain(q1, q2)])
    for recipient in recipients:
        item = Notification(event=event, recipient_id=recipient)
        db.session.add(item)
