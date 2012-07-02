# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.types import Integer, Float, String, DateTime
from skylines.model import DeclarativeBase, DBSession
from tg import config, request
from geoalchemy.geometry import GeometryColumn, Point, GeometryDDL
from geoalchemy.postgis import PGComparator
from geoalchemy.functions import functions
from skylines.model.geo import Location


class Airport(DeclarativeBase):
    __tablename__ = 'airports'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time_created = Column(DateTime, nullable=False, default=datetime.now)
    time_modified = Column(DateTime, nullable=False, default=datetime.now)

    location_wkt = GeometryColumn(Point(2), comparator=PGComparator)
    altitude = Column(Float)

    name = Column(String(), nullable=False)
    short_name = Column(String())
    icao = Column(String(4))
    country_code = Column(String(2), nullable=False)

    surface = Column(String(10))
    runway_len = Column(Integer)
    runway_dir = Column(Integer)
    frequency = Column(Float)
    type = Column(String(20))

    @property
    def location(self):
        if self.location_wkt is None:
            return None

        wkt = DBSession.scalar(self.location_wkt.wkt)
        return Location.from_wkt(wkt)

    @location.setter
    def location(self, location):
        if location is None:
            self.location_wkt = None
        else:
            self.location_wkt = location.to_wkt()

    @classmethod
    def by_location(cls, location):
        if location is None:
            return None

        airport = DBSession.query(cls, functions.distance(cls.location_wkt, location.to_wkt()).label('distance'))\
            .order_by(functions.distance(cls.location_wkt, location.to_wkt())).first()

        if airport and airport.distance < 0.01:
            return airport.Airport
        else:
            return None

GeometryDDL(Airport.__table__)
