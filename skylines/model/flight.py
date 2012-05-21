# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from auth import User
from skylines.model import DeclarativeBase

class Flight(DeclarativeBase):
    __tablename__ = 'flights'

    id = Column(Integer, autoincrement=True, primary_key=True)
    owner_id = Column(Integer, ForeignKey('tg_user.user_id'), nullable=False)
    owner = relation('User', primaryjoin=(owner_id==User.user_id))
    time_created = Column(DateTime, nullable=False, default=datetime.now)
    time_modified = Column(DateTime, nullable=False, default=datetime.now)
    filename = Column(String(), nullable=False)
