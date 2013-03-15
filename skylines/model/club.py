# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, DateTime
from skylines.model.base import DeclarativeBase
from skylines.model.auth import User


class Club(DeclarativeBase):
    __tablename__ = 'clubs'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)

    owner_id = Column(Integer, ForeignKey('tg_user.id', use_alter=True,
                                          name="tg_user.id"))

    owner = relation('User', primaryjoin=(owner_id == User.id))

    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)

    website = Column(Unicode(255))

    members = relation('User', primaryjoin=(User.club_id == id),
                       order_by=(User.display_name),
                       backref='club', post_update=True)
    flights = relation('Flight', backref='club')

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return ('<Club: id=%d name=\'%s\'>' % (self.id, self.name)).encode('utf-8')

    def is_writable(self, identity):
        return identity and \
            (self.id == identity['user'].club_id or
             'manage' in identity['permissions'])
