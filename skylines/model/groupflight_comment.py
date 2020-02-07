from datetime import datetime

from sqlalchemy.types import Unicode, Integer, DateTime

from skylines.database import db
from skylines.lib.string import unicode_to_str


class GroupflightComment(db.Model):
    __tablename__ = "groupflight_comments"

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    groupflight_id = db.Column(
        Integer,
        db.ForeignKey("groupflights.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    groupflight = db.relationship(
        "Groupflight",
        innerjoin=True,
        backref=db.backref("comments", order_by=time_created, passive_deletes=True),
    )

    user_id = db.Column(Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    user = db.relationship("User", lazy="joined")

    text = db.Column(Unicode, nullable=False)

    def __repr__(self):
        return unicode_to_str(
            "<GroupflightComment: id=%d user_id=%d groupflight_id=%d>"
            % (self.id, self.user_id, self.groupflight_id)
        )
