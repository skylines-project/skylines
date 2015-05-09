# -*- coding: utf-8 -*-

from sqlalchemy.types import String, Integer, Interval, DateTime
from geoalchemy2.types import Geometry
from geoalchemy2.shape import to_shape

from skylines.database import db
from .geo import Location


class ContestLeg(db.Model):
    """
    This table saves the legs of a optimized Flight.
    """

    __tablename__ = 'contest_legs'

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    flight_id = db.Column(
        Integer, db.ForeignKey('flights.id', ondelete='CASCADE'), nullable=False,
        index=True)
    flight = db.relationship(
        'Flight', innerjoin=True,
        backref=db.backref('_legs', passive_deletes=True,
                           cascade='all, delete, delete-orphan'))

    contest_type = db.Column(String, nullable=False)
    trace_type = db.Column(String, nullable=False)

    # direct distance from start to end
    distance = db.Column(Integer)

    # total height and duration of cruise phases
    cruise_height = db.Column(Integer)
    cruise_distance = db.Column(Integer)
    cruise_duration = db.Column(Interval)

    # total height and duration of climb phases
    climb_height = db.Column(Integer)
    climb_duration = db.Column(Interval)

    # start and end height
    start_height = db.Column(Integer)
    end_height = db.Column(Integer)

    # start and end time
    start_time = db.Column(DateTime, nullable=False)
    end_time = db.Column(DateTime, nullable=False)

    # start and end locations
    start_location_wkt = db.Column(
        'start_location', Geometry('POINT', srid=4326))
    end_location_wkt = db.Column(
        'end_location', Geometry('POINT', srid=4326))

    @property
    def duration(self):
        return self.end_time - self.start_time

    @property
    def speed(self):
        if self.distance is None:
            return None

        return float(self.distance) / self.duration.total_seconds()

    @property
    def start_location(self):
        if self.start_location_wkt is None:
            return None

        coords = to_shape(self.start_location_wkt)
        return Location(latitude=coords.y, longitude=coords.x)

    @start_location.setter
    def start_location(self, location):
        if location is None:
            self.start_location_wkt = None
        else:
            self.start_location_wkt = location.to_wkt_element()

    @property
    def end_location(self):
        if self.end_location_wkt is None:
            return None

        coords = to_shape(self.end_location_wkt)
        return Location(latitude=coords.y, longitude=coords.x)

    @end_location.setter
    def end_location(self, location):
        if location is None:
            self.end_location_wkt = None
        else:
            self.end_location_wkt = location.to_wkt_element()
