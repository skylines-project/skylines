# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.sql.expression import func
from geoalchemy2.types import Geometry
from geoalchemy2.elements import WKTElement

from .base import DeclarativeBase


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

    @classmethod
    def get_info(cls, location):
        '''Returns a query object of all airspaces at the location'''
        return cls.query() \
            .filter(func.ST_Intersects(WKTElement(location.to_wkt(), srid=4326), cls.the_geom))
