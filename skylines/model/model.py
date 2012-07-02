# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode
from skylines.model import DeclarativeBase


class Model(DeclarativeBase):
    __tablename__ = 'models'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64), unique=True, nullable=False)

    # the kind of aircraft: 0=unspecified, 1=glider, 2=motor glider,
    # 3=self-launching glider, 4=self-sustaining glider, 5=paraglider,
    kind = Column(Integer, nullable=False, default=0)

    igc_index = Column(Integer)

    # the index for the German DMSt
    dmst_index = Column(Integer)

    def __unicode__(self):
        return self.name

    def is_writable(self):
        from tg import request
        return request.identity and \
                   'manage' in request.identity['permissions']

    @classmethod
    def by_name(cls, _name):
        from skylines.model import DBSession
        return DBSession.query(cls).filter_by(name=_name).first()
