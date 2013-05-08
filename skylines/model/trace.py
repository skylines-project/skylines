# -*- coding: utf-8 -*-

from sqlalchemy import ForeignKey, Column
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import String, Integer, DateTime, Interval
from sqlalchemy.schema import Index
from geoalchemy2.types import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

from .base import DeclarativeBase
from .geo import Location


class Trace(DeclarativeBase):
    """
    This table saves the locations and visiting times of the turnpoints
    of an optimized Flight.
    """

    __tablename__ = 'traces'

    id = Column(Integer, autoincrement=True, primary_key=True)

    flight_id = Column(Integer, ForeignKey('flights.id', ondelete='CASCADE'),
                       nullable=False)
    flight = relationship('Flight', backref=backref('traces', cascade="all"))

    contest_type = Column(String, nullable=False)
    trace_type = Column(String, nullable=False)

    distance = Column(Integer)
    duration = Column(Interval)

    times = Column(postgresql.ARRAY(DateTime), nullable=False)
    _locations = Column(
        'locations', Geometry('LINESTRING', management=True), nullable=False)

    @property
    def speed(self):
        if self.distance is None or self.duration is None:
            return None

        return float(self.distance) / self.duration.total_seconds()

    @property
    def locations(self):
        return [Location(longitude=location[0], latitude=location[1])
                for location in to_shape(self._locations).coords]

    @locations.setter
    def locations(self, locations):
        points = ['{} {}'.format(location.longitude, location.latitude)
                  for location in locations]
        wkt = "LINESTRING({})".format(','.join(points))
        self._locations = WKTElement(wkt, srid=4326)

Index('traces_contest_idx',
      Trace.flight_id, Trace.contest_type, Trace.trace_type,
      unique=True)
