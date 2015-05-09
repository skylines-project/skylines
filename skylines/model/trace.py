# -*- coding: utf-8 -*-

from sqlalchemy.dialects import postgresql
from sqlalchemy.types import String, Integer, DateTime, Interval
from geoalchemy2.types import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

from skylines.database import db
from .geo import Location


class Trace(db.Model):
    """
    This table saves the locations and visiting times of the turnpoints
    of an optimized Flight.
    """

    __tablename__ = 'traces'

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    flight_id = db.Column(
        Integer, db.ForeignKey('flights.id', ondelete='CASCADE'), nullable=False)
    flight = db.relationship(
        'Flight', innerjoin=True,
        backref=db.backref('traces', passive_deletes=True))

    contest_type = db.Column(String, nullable=False)
    trace_type = db.Column(String, nullable=False)

    distance = db.Column(Integer)
    duration = db.Column(Interval)

    times = db.Column(postgresql.ARRAY(DateTime), nullable=False)
    _locations = db.Column(
        'locations', Geometry('LINESTRING', srid=4326), nullable=False)

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

db.Index('traces_contest_idx',
         Trace.flight_id, Trace.contest_type, Trace.trace_type,
         unique=True)
