# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.types import Integer, Float, String, DateTime
from sqlalchemy.sql.expression import cast, func
from geoalchemy2.types import Geography, Geometry
from geoalchemy2.elements import WKTElement

from .base import DeclarativeBase
from .session import DBSession


class MountainWaveProject(DeclarativeBase):
    __tablename__ = 'mountain_wave_project'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = Column(DateTime, nullable=False, default=datetime.utcnow)

    location = Column(Geometry('POINT', srid=4326))
    axis = Column(Geometry('LINESTRING', srid=4326))
    ellipse = Column(Geometry('LINESTRING', srid=4326))

    name = Column(String())
    country_code = Column(String(2))
    vertical = Column(Float)
    synoptical = Column(String(254))
    main_wind_direction = Column(String(254))
    additional = Column(String(254))
    source = Column(String(254))
    remark1 = Column(String(254))
    remark2 = Column(String(254))
    orientation = Column(Float)
    rotor_height = Column(String(254))
    weather_dir = Column(Integer)
    axis_length = Column(Float)

    def __repr__(self):
        return ('<MountainWaveProject: id=%d name=\'%s\'>' % (self.id, self.name)).encode('utf-8')

    @classmethod
    def get_info(cls, location):
        '''Returns a query object of mountain waves around the location'''
        return DBSession.query(cls) \
            .filter(func.ST_DWithin(
                cast(WKTElement(location.to_wkt(), srid=4326), Geography),
                cast(cls.location, Geography),
                5000))
