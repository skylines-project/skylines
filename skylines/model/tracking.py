# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from sqlalchemy.orm import relation, joinedload
from sqlalchemy import Column, ForeignKey, Index, over, func
from sqlalchemy.types import Integer, Float, DateTime, SmallInteger, Unicode,\
    BigInteger
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql.expression import desc
from geoalchemy2.types import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from skylines.model.base import DeclarativeBase
from skylines.model.session import DBSession
from skylines.model.auth import User
from skylines.model.geo import Location


class TrackingFix(DeclarativeBase):
    __tablename__ = 'tracking_fixes'

    id = Column(Integer, autoincrement=True, primary_key=True)

    time = Column(DateTime, nullable=False, default=datetime.utcnow)

    location_wkt = Column('location', Geometry('POINT', management=True))

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

        coords = to_shape(self.location_wkt).coords[0]
        return Location(latitude=coords[1], longitude=coords[0])

    @location.setter
    def location(self, location):
        self.location_wkt = WKTElement(location.to_wkt())

    @classmethod
    def max_age_filter(cls, max_age=timedelta(hours=6)):
        return TrackingFix.time >= datetime.utcnow() - max_age

    @classmethod
    def delay_filter(cls, delay):
        return TrackingFix.time <= datetime.utcnow() - delay

    @classmethod
    def get_latest(cls, max_age=timedelta(hours=6)):
        # Add a column to the inner query with
        # numbers ordered by time for each pilot
        row_number = over(func.row_number(),
                          partition_by=cls.pilot_id,
                          order_by=desc(cls.time))

        # Create inner query
        subq = DBSession \
            .query(cls.id, row_number.label('row_number')) \
            .outerjoin(cls.pilot) \
            .filter(cls.max_age_filter(max_age)) \
            .filter(cls.delay_filter(User.tracking_delay_interval())) \
            .filter(cls.location_wkt != None) \
            .subquery()

        # Create outer query that orders by time and
        # only selects the latest fix
        query = DBSession \
            .query(cls) \
            .options(joinedload(cls.pilot)) \
            .filter(cls.id == subq.c.id) \
            .filter(subq.c.row_number == 1) \
            .order_by(desc(cls.time))

        return query


Index('tracking_fixes_pilot_time', TrackingFix.pilot_id, TrackingFix.time)


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
