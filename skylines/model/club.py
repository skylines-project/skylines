# -*- coding: utf-8 -*-

from sqlalchemy import *
from sqlalchemy.orm import relation
from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode
from skylines.model import DeclarativeBase

class Club(DeclarativeBase):
    __tablename__ = 'clubs'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)

    members = relation('User', backref='club')
    flights = relation('Flight', backref='club')

    def __unicode__(self):
        return self.name

    def is_writable(self):
        from tg import request
        return request.identity and \
               (self.id == request.identity['user'].club_id or
                'manage' in request.identity['permissions'])
