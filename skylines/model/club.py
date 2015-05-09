# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.types import Integer, Unicode, DateTime

from skylines.database import db


class Club(db.Model):
    __tablename__ = 'clubs'
    __searchable_columns__ = ['name']
    __search_detail_columns__ = ['website']

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    name = db.Column(Unicode(255), unique=True, nullable=False)

    owner_id = db.Column(Integer, db.ForeignKey(
        'users.id', use_alter=True, name="users.id", ondelete='SET NULL'))
    owner = db.relationship('User', foreign_keys=[owner_id])

    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    website = db.Column(Unicode(255))

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return ('<Club: id=%d name=\'%s\'>' % (self.id, self.name)).encode('unicode_escape')

    def is_writable(self, user):
        return user and (self.id == user.club_id or user.is_manager())
