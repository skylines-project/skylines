# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, DateTime
from skylines.model.auth import User
from skylines.model import DeclarativeBase
from tg import request


class Club(DeclarativeBase):
    __tablename__ = 'clubs'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)

    owner_id = Column(Integer, ForeignKey('tg_user.user_id', use_alter=True,
                                           name="tg_user.user_id"))

    owner = relation('User', primaryjoin=(owner_id == User.user_id))

    time_created = Column(DateTime, nullable=False, default=datetime.now)

    website = Column(Unicode(255))

    members = relation('User', primaryjoin=(User.club_id == id),
                       order_by=(User.display_name),
                       backref='club', post_update=True)
    flights = relation('Flight', backref='club')

    def __unicode__(self):
        return self.name

    def is_writable(self):
        return request.identity and \
               (self.id == request.identity['user'].club_id or
                'manage' in request.identity['permissions'])
