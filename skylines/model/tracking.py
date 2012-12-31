# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.types import Integer, Float, DateTime
from sqlalchemy.dialects.postgresql import INET
from geoalchemy.geometry import GeometryColumn, Point, GeometryDDL
from geoalchemy.postgis import PGComparator
from skylines.model.base import DeclarativeBase
from skylines.model.session import DBSession
from skylines.model.auth import User
from skylines.model.geo import Location


class TrackingFix(DeclarativeBase):
    __tablename__ = 'tracking_fixes'

    id = Column(Integer, autoincrement=True, primary_key=True)

    time = Column(DateTime, nullable=False, default=datetime.utcnow)

    location_wkt = GeometryColumn('location', Point(2, wkt_internal=True),
                                  comparator=PGComparator)

    track = Column(Integer)
    ground_speed = Column(Float)
    airspeed = Column(Float)
    altitude = Column(Integer)
    vario = Column(Float)
    engine_noise_level = Column(Integer)

    pilot_id = Column(Integer,
                      ForeignKey('tg_user.id', use_alter=True,
                                 name="tg_user.id"), nullable=False)

    pilot = relation('User', primaryjoin=(pilot_id == User.id))

    ip = Column(INET)

    def __repr__(self):
        return ('<TrackingFix: id=%d time=\'%s\'>' % (self.id, self.time)).encode('utf-8')

    @property
    def location(self):
        if self.location_wkt is None:
            return None

        coords = self.location_wkt.coords(DBSession)
        return Location(latitude=coords[1], longitude=coords[0])

    @location.setter
    def location(self, location):
        self.location_wkt = location.to_wkt()

Index('tracking_fixes_pilot_time', TrackingFix.pilot_id, TrackingFix.time)
GeometryDDL(TrackingFix.__table__)
