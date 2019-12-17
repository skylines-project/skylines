# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.types import Integer, Unicode, DateTime

from skylines.database import db
from skylines.lib.string import unicode_to_str
from skylines.lib.sql import LowerCaseComparator

class Club(db.Model):
    __tablename__ = "clubs"
    __searchable_columns__ = ["name"]
    __search_detail_columns__ = ["website"]
    __search_detail_columns__ = ["email_address"]

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    name = db.Column(Unicode(255), unique=True, nullable=False)
    email_address = db.column_property(
        db.Column(Unicode(255)), comparator_factory=LowerCaseComparator
    )
    owner_id = db.Column(
        Integer,
        db.ForeignKey("users.id", use_alter=True, name="users.id", ondelete="SET NULL"),
    )
    owner = db.relationship("User", foreign_keys=[owner_id])

    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    website = db.Column(Unicode(255))

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return unicode_to_str("<Club: id=%d name='%s'>" % (self.id, self.name))

    def is_writable(self, user):
        return user and (self.id == user.club_id or user.is_manager())
