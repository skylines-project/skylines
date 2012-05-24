# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from auth import User
from skylines.model import DeclarativeBase, DBSession

class Flight(DeclarativeBase):
    __tablename__ = 'flights'

    id = Column(Integer, autoincrement=True, primary_key=True)
    owner_id = Column(Integer, ForeignKey('tg_user.user_id'), nullable=False)
    owner = relation('User', primaryjoin=(owner_id==User.user_id))
    time_created = Column(DateTime, nullable=False, default=datetime.now)
    time_modified = Column(DateTime, nullable=False, default=datetime.now)
    filename = Column(String(), nullable=False)
    md5 = Column(String(32), nullable=False, unique=True)

    pilot_id = Column(Integer, ForeignKey('tg_user.user_id'))
    pilot = relation('User', primaryjoin=(pilot_id==User.user_id))
    co_pilot_id = Column(Integer, ForeignKey('tg_user.user_id'))
    co_pilot = relation('User', primaryjoin=(co_pilot_id==User.user_id))

    club_id = Column(Integer, ForeignKey('clubs.id'))

    takeoff_time = Column(DateTime, nullable=False)
    landing_time = Column(DateTime, nullable=False)

    olc_classic_distance = Column(Integer)
    olc_triangle_distance = Column(Integer)
    olc_plus_score = Column(Integer)

    @classmethod
    def by_md5(cls, _md5):
        return DBSession.query(cls).filter_by(md5=_md5).first()

    def get_download_uri(self):
        from tg import config
        return config['skylines.files.uri'] + '/' + self.filename

    def is_writable(self):
        from tg import request
        return request.identity and \
               (self.owner_id == request.identity['user'].user_id or
                self.pilot_id == request.identity['user'].user_id or
                'manage' in request.identity['permissions'])
