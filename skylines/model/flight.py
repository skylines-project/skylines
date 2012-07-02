# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import ForeignKey, Column, func
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from skylines.model.auth import User
from skylines.model import DeclarativeBase, DBSession
from tg import config, request
from geoalchemy.geometry import GeometryColumn, Point, GeometryDDL
from geoalchemy.postgis import PGComparator
from skylines.model.geo import Location
from skylines.model.igcfile import IGCFile
from skylines.model.model import Model
from skylines.model.airport import Airport

class Flight(DeclarativeBase):
    __tablename__ = 'flights'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time_created = Column(DateTime, nullable=False, default=datetime.now)
    time_modified = Column(DateTime, nullable=False, default=datetime.now)

    pilot_id = Column(Integer, ForeignKey('tg_user.user_id'))
    pilot = relation('User', primaryjoin=(pilot_id == User.user_id))
    co_pilot_id = Column(Integer, ForeignKey('tg_user.user_id'))
    co_pilot = relation('User', primaryjoin=(co_pilot_id == User.user_id))

    club_id = Column(Integer, ForeignKey('clubs.id'))

    model_id = Column(Integer, ForeignKey('models.id'))
    model = relation('Model', primaryjoin=(model_id==Model.id))
    registration = Column(Unicode(32))

    takeoff_time = Column(DateTime, nullable=False)
    landing_time = Column(DateTime, nullable=False)
    takeoff_location_wkt = GeometryColumn(Point(2), comparator=PGComparator)
    landing_location_wkt = GeometryColumn(Point(2), comparator=PGComparator)

    takeoff_airport_id = Column(Integer, ForeignKey('airports.id'))
    takeoff_airport = relation('Airport', primaryjoin=(takeoff_airport_id == Airport.id))

    olc_classic_distance = Column(Integer)
    olc_triangle_distance = Column(Integer)
    olc_plus_score = Column(Integer)

    igc_file_id = Column(Integer, ForeignKey('igc_files.id'))
    igc_file = relation('IGCFile', primaryjoin=(igc_file_id == IGCFile.id),
                        backref='flights')

    @hybrid_property
    def duration(self):
        return self.landing_time - self.takeoff_time

    @hybrid_property
    def year(self):
        return self.takeoff_time.year

    @year.expression
    def year(cls):
        return func.date_part('year', cls.takeoff_time)

    @property
    def takeoff_location(self):
        if self.takeoff_location_wkt is None:
            return None

        wkt = DBSession.scalar(self.takeoff_location_wkt.wkt)
        return Location.from_wkt(wkt)

    @takeoff_location.setter
    def takeoff_location(self, location):
        if location is None:
            self.takeoff_location_wkt = None
        else:
            self.takeoff_location_wkt = location.to_wkt()

    @property
    def landing_location(self):
        if self.landing_location_wkt is None:
            return None

        wkt = DBSession.scalar(self.landing_location_wkt.wkt)
        return Location.from_wkt(wkt)

    @landing_location.setter
    def landing_location(self, location):
        if location is None:
            self.landing_location_wkt = None
        else:
            self.landing_location_wkt = location.to_wkt()

    @classmethod
    def by_md5(cls, _md5):
        file = IGCFile.by_md5(_md5)
        if file is None:
            return None

        return DBSession.query(cls).filter_by(igc_file=file).first()

    def is_writable(self):
        return request.identity and \
               (self.igc_file.owner_id == request.identity['user'].user_id or
                self.pilot_id == request.identity['user'].user_id or
                'manage' in request.identity['permissions'])

    def may_delete(self):
        return request.identity and 'manage' in request.identity['permissions']

GeometryDDL(Flight.__table__)
