# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.types import Integer, Float, DateTime, SmallInteger, Unicode,\
    BigInteger
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql.expression import desc
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
        return '<TrackingFix: id={} time=\'{}\'>' \
               .format(self.id, self.time).encode('utf-8')

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


class TrackingSession(DeclarativeBase):
    __tablename__ = 'tracking_sessions'

    id = Column(Integer, autoincrement=True, primary_key=True)

    pilot_id = Column(Integer,
                      ForeignKey('tg_user.id', use_alter=True,
                                 name="tg_user.id"), nullable=False)

    pilot = relation('User', primaryjoin=(pilot_id == User.id))

    lt24_id = Column(BigInteger, index=True)

    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    ip_created = Column(INET)

    time_finished = Column(DateTime)
    ip_finished = Column(INET)

    # client application
    client = Column(Unicode(32))
    client_version = Column(Unicode(8))

    # device information
    device = Column(Unicode(32))
    gps_device = Column(Unicode(32))

    # aircraft information
    aircraft_type = Column(SmallInteger)
    aircraft_model = Column(Unicode(64))

    # status of the pilot after landing
    #
    # 0-> "Everything OK"
    # 1-> "Need retrieve"
    # 2-> "Need some help, nothing broken"
    # 3-> "Need help, maybe something broken"
    # 4-> "HELP, SERIOUS INJURY"
    finish_status = Column(SmallInteger)

    def __repr__(self):
        return '<TrackingSession: id={}>'.format(self.id).encode('utf-8')

    @classmethod
    def by_lt24_id(cls, lt24_id, filter_finished=True):
        query = DBSession.query(cls).filter_by(lt24_id=lt24_id)
        if filter_finished:
            query = query.filter_by(time_finished=None)

        return query.order_by(desc(cls.time_created)).first()
