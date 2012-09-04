from datetime import datetime
from sets import Set

from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer, DateTime

from skylines.model import DeclarativeBase, DBSession
from skylines.model import User, Flight, FlightComment


class Notification(DeclarativeBase):
    __tablename__ = 'notifications'

    id = Column(Integer, autoincrement=True, primary_key=True)

    # Time stamps
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_read = Column(DateTime)

    # The user that caused the notification (if any)
    sender_id = Column(Integer,
                       ForeignKey('tg_user.user_id', ondelete='CASCADE'),
                       nullable=False)

    sender = relation('User', primaryjoin=(sender_id == User.user_id))

    # The recipient of this notification
    recipient_id = Column(Integer,
                          ForeignKey('tg_user.user_id', ondelete='CASCADE'),
                          nullable=False)

    recipient = relation('User', primaryjoin=(recipient_id == User.user_id))

    # A flight if this notification is about a flight
    flight_id = Column(Integer, ForeignKey('flights.id', ondelete='CASCADE'))
    flight = relation('Flight', primaryjoin=(flight_id == Flight.id))

    # A flight comment if this notification is about a flight comment
    flight_comment_id = Column(Integer,
                               ForeignKey('flight_comments.id', ondelete='CASCADE'))

    flight_comment = relation('FlightComment',
                              primaryjoin=(flight_comment_id == FlightComment.id))

    def mark_read(self):
        self.time_read = datetime.utcnow()

    @classmethod
    def mark_all_read(cls, user):
        DBSession.query(cls) \
                 .filter(cls.recipient == user) \
                 .update(dict(time_read=datetime.utcnow()))


def count_unread_notifications(user):
    return DBSession.query(Notification) \
                    .filter(Notification.recipient == user) \
                    .filter(Notification.time_read == None).count()


def create_flight_comment_notifications(comment):
    '''
    Create notifications for the owner and pilots of the flight
    '''

    # Create list of potential recipients (using Set to avoid duplicates)
    recipients = Set([comment.flight.igc_file.owner,
                      comment.flight.pilot,
                      comment.flight.co_pilot])

    # Create notifications for the recipients in the Set
    for recipient in recipients:
        # There is no need to notify the user that caused the notification
        if recipient is None or recipient == comment.user:
            continue

        item = Notification(sender=comment.user,
                            recipient=recipient,
                            flight=comment.flight,
                            flight_comment=comment)
        DBSession.add(item)
