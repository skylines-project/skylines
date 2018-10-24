from datetime import datetime

from sqlalchemy.types import Integer, DateTime

from skylines.database import db
from skylines.lib.string import unicode_to_str


class Event(db.Model):
    __tablename__ = "events"

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
        Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    actor = db.relationship("User", foreign_keys=[actor_id], innerjoin=True)

    # A user if this event is about a user (e.g. actor following user)

    user_id = db.Column(Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    user = db.relationship("User", foreign_keys=[user_id])

    # A club if this event is about a club (e.g. actor joining club)

    club_id = db.Column(Integer, db.ForeignKey("clubs.id", ondelete="CASCADE"))
    club = db.relationship("Club")

    # A flight if this event is about a flight

    flight_id = db.Column(Integer, db.ForeignKey("flights.id", ondelete="CASCADE"))
    flight = db.relationship("Flight")

    # A flight comment if this event is about a flight comment

    flight_comment_id = db.Column(
        Integer, db.ForeignKey("flight_comments.id", ondelete="CASCADE")
    )
    flight_comment = db.relationship("FlightComment")

    ##############################

    def __repr__(self):
        return unicode_to_str("<Event: id={} type={}>".format(self.id, self.type))

    ##############################

    @staticmethod
    def for_flight_comment(comment):
        """
        Create notifications for the owner and pilots of the flight
        """
        return Event(
            type=Event.Type.FLIGHT_COMMENT,
            actor=comment.user,
            flight=comment.flight,
            flight_comment=comment,
        )

    @staticmethod
    def for_flight(flight):
        """
        Create notifications for the followers of the owner and pilots of the flight
        """
        return Event(
            type=Event.Type.FLIGHT, actor_id=flight.igc_file.owner_id, flight=flight
        )

    @staticmethod
    def for_follower(followed, follower):
        """
        Create event for the followed pilot about his new follower
        """
        return Event(type=Event.Type.FOLLOWER, actor=follower, user=followed)

    @staticmethod
    def for_new_user(user):
        """
        Create event for a new SkyLines user.
        """
        return Event(type=Event.Type.NEW_USER, actor=user)

    @staticmethod
    def for_club_join(club_id, user):
        """
        Create event for a user joining a club.
        """
        return Event(type=Event.Type.CLUB_JOIN, actor=user, club_id=club_id)
