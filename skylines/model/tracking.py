# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Float, DateTime
from geoalchemy.geometry import GeometryColumn, Point, GeometryDDL
from geoalchemy.postgis import PGComparator
from skylines.model.auth import User
from skylines.model import DeclarativeBase, DBSession
from skylines.model.geo import Location

class TrackingFix(DeclarativeBase):
    __tablename__ = 'tracking_fixes'

    id = Column(Integer, autoincrement=True, primary_key=True)

    time = Column(DateTime, nullable=False, default=datetime.now)

    location_wkt = GeometryColumn(Point(2), comparator=PGComparator)

    track = Column(Integer)
    ground_speed = Column(Float)
    airspeed = Column(Float)
    altitude = Column(Integer)
    vario = Column(Float)
    engine_noise_level = Column(Integer)

    pilot_id = Column(Integer,
                      ForeignKey('tg_user.user_id', use_alter=True,
                                 name="tg_user.user_id"), nullable=False)

    pilot = relation('User', primaryjoin=(pilot_id == User.user_id))

    @property
    def location(self):
        if self.location_wkt is None:
            return None

        wkt = DBSession.scalar(self.location_wkt.wkt)
        return Location.from_wkt(wkt)

    @location.setter
    def location(self, location):
        self.location_wkt = location.to_wkt()

GeometryDDL(TrackingFix.__table__)
