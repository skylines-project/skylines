from datetime import datetime

from sqlalchemy.types import Integer, DateTime

from skylines import db


class Follower(db.Model):
    __tablename__ = 'followers'
    __table_args__ = (
        db.UniqueConstraint('source_id', 'destination_id', name='unique_connection'),
    )

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    source_id = db.Column(
        Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True, nullable=False)
    source = db.relationship(
        'User', foreign_keys=[source_id],
        lazy='joined', backref='following')

    destination_id = db.Column(
        Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        index=True, nullable=False)
    destination = db.relationship(
        'User', foreign_keys=[destination_id],
        lazy='joined', backref='followers')

    time = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def follows(cls, source, destination):
        return cls.query(source=source, destination=destination).count() > 0

    @classmethod
    def follow(cls, source, destination):
        f = cls.query(source=source, destination=destination).first()
        if not f:
            f = Follower(source=source, destination=destination)
            db.session.add(f)

    @classmethod
    def unfollow(cls, source, destination):
        cls.query(source=source, destination=destination).delete()
