# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import ForeignKey, Column
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relation
from sqlalchemy.types import String, Integer, DateTime
from geoalchemy import WKTSpatialElement
from geoalchemy.geometry import GeometryColumn, LineString, GeometryDDL
from geoalchemy.postgis import PGComparator

from skylines.model import DeclarativeBase, DBSession
from skylines.model.flight import Flight
from skylines.model.geo import Location


class Trace(DeclarativeBase):
    """
    This table saves the locations and visiting times of the turnpoints
    of an optimized Flight.
    """

    __tablename__ = 'traces'

    id = Column(Integer, autoincrement=True, primary_key=True)

    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    flight = relation('Flight', primaryjoin=(flight_id == Flight.id),
                      backref='traces')

    contest_type = Column(String, nullable=False)
    trace_type = Column(String, nullable=False)

    times = Column(postgresql.ARRAY(DateTime), nullable=False)
    _locations = GeometryColumn('locations', LineString(2),
                                nullable=False, comparator=PGComparator)

    @property
    def locations(self):
        return [Location(longitude=location[0], latitude=location[1])
                for location in self._locations.coords(DBSession)]

    @locations.setter
    def locations(self, locations):
        points = []
        for location in locations:
            points.append('{} {}'.format(location.longitude, location.latitude))

        wkt = "LINESTRING({})".format(','.join(points))
        self._locations = WKTSpatialElement(wkt)

GeometryDDL(Trace.__table__)
