# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import Integer, String, DateTime
from skylines.model.base import DeclarativeBase
from geoalchemy2.types import Geometry


class Airspace(DeclarativeBase):
    __tablename__ = 'airspace'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = Column(DateTime, nullable=False, default=datetime.utcnow)

    the_geom = Column(Geometry('POLYGON', management=True))

    name = Column(String(), nullable=False)
    airspace_class = Column(String(3), nullable=False)
    base = Column(String(30), nullable=False)
    top = Column(String(30), nullable=False)
    country_code = Column(String(2), nullable=False)

    def __repr__(self):
        return ('<Airspace: id=%d name=\'%s\'>' % (self.id, self.name)).encode('utf-8')
