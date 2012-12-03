# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm import relation
from sqlalchemy import ForeignKey, Column, func
from sqlalchemy.types import Unicode, Integer, DateTime, Date, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import desc, case
from tg import request
from geoalchemy.geometry import GeometryColumn, Point, GeometryDDL
from geoalchemy.postgis import PGComparator
from skylines.model.base import DeclarativeBase
from skylines.model.session import DBSession
from skylines.model.auth import User
from skylines.model.geo import Location
from skylines.model.igcfile import IGCFile
from skylines.model.aircraft_model import AircraftModel
from skylines.model.airport import Airport


class Flight(DeclarativeBase):
    __tablename__ = 'flights'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = Column(DateTime, nullable=False, default=datetime.utcnow)

    pilot_id = Column(Integer, ForeignKey('tg_user.id'), index=True)
    pilot = relation('User', primaryjoin=(pilot_id == User.id))
    co_pilot_id = Column(Integer, ForeignKey('tg_user.id'), index=True)
    co_pilot = relation('User', primaryjoin=(co_pilot_id == User.id))

    club_id = Column(Integer, ForeignKey('clubs.id'), index=True)

    model_id = Column(Integer, ForeignKey('models.id'))
    model = relation('AircraftModel', primaryjoin=(model_id == AircraftModel.id))
    registration = Column(Unicode(32))
    competition_id = Column(Unicode(5))

    # The date of the flight in local time instead of UTC. Used for scoring.
    date_local = Column(Date, nullable=False, index=True)

    takeoff_time = Column(DateTime, nullable=False, index=True)
    landing_time = Column(DateTime, nullable=False)
    takeoff_location_wkt = GeometryColumn('takeoff_location',
                                          Point(2, wkt_internal=True),
                                          comparator=PGComparator)
    landing_location_wkt = GeometryColumn('landing_location',
                                          Point(2, wkt_internal=True),
                                          comparator=PGComparator)

    takeoff_airport_id = Column(Integer, ForeignKey('airports.id'))
    takeoff_airport = relation('Airport',
                               primaryjoin=(takeoff_airport_id == Airport.id))

    landing_airport_id = Column(Integer, ForeignKey('airports.id'))
    landing_airport = relation('Airport',
                               primaryjoin=(landing_airport_id == Airport.id))

    olc_classic_distance = Column(Integer)
    olc_triangle_distance = Column(Integer)
    olc_plus_score = Column(Integer)

    igc_file_id = Column(Integer, ForeignKey('igc_files.id'))
    igc_file = relation('IGCFile', primaryjoin=(igc_file_id == IGCFile.id),
                        backref='flights')

    needs_analysis = Column(Boolean, nullable=False, default=True)

    @hybrid_property
    def duration(self):
        return self.landing_time - self.takeoff_time

    @hybrid_property
    def year(self):
        return self.date_local.year

    @hybrid_property
    def index_score(self):
        if self.model and self.model.dmst_index > 0:
            return self.olc_plus_score * 100 / self.model.dmst_index
        else:
            return self.olc_plus_score

    @index_score.expression
    def index_score(cls):
        return case([(AircraftModel.dmst_index > 0,  cls.olc_plus_score * 100 / AircraftModel.dmst_index)], else_=cls.olc_plus_score)

    @year.expression
    def year(cls):
        return func.date_part('year', cls.date_local)

    @property
    def takeoff_location(self):
        if self.takeoff_location_wkt is None:
            return None

        coords = self.takeoff_location_wkt.coords(DBSession)
        return Location(latitude=coords[1], longitude=coords[0])

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

        coords = self.landing_location_wkt.coords(DBSession)
        return Location(latitude=coords[1], longitude=coords[0])

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
               (self.igc_file.owner_id == request.identity['user'].id or
                self.pilot_id == request.identity['user'].id or
                'manage' in request.identity['permissions'])

    def may_delete(self):
        return request.identity and \
               (self.igc_file.owner_id == request.identity['user'].id or
               'manage' in request.identity['permissions'])

    @classmethod
    def get_largest(cls):
        '''Returns a query object ordered by distance'''
        return DBSession.query(cls).order_by(desc(cls.olc_classic_distance))

    def get_optimised_contest_trace(self, contest_type, trace_type):
        from skylines.model.trace import Trace
        query = DBSession.query(Trace) \
                    .filter(Trace.contest_type == contest_type) \
                    .filter(Trace.trace_type == trace_type) \
                    .filter(Trace.flight == self).first()
        return query

    def get_contest_speed(self, contest_type, trace_type):
        contest = self.get_optimised_contest_trace(contest_type, trace_type)
        return contest and contest.speed

    @property
    def speed(self):
        return self.get_contest_speed('olc_plus', 'classic')

    @property
    def has_phases(self):
        return bool(self._phases)

    @property
    def phases(self):
        return [p for p in self._phases if not p.aggregate]

    def delete_phases(self):
        from skylines.model.flight_phase import FlightPhase
        DBSession.query(FlightPhase) \
            .filter(FlightPhase.flight == self) \
            .delete()

    @property
    def circling_performance(self):
        from skylines.model.flight_phase import FlightPhase
        stats = [p for p in self._phases
                 if (p.aggregate
                     and p.phase_type == FlightPhase.PT_CIRCLING
                     and p.duration.total_seconds() > 0)]
        order = [FlightPhase.CD_TOTAL,
                 FlightPhase.CD_LEFT,
                 FlightPhase.CD_RIGHT,
                 FlightPhase.CD_MIXED]
        stats.sort(lambda a, b: cmp(order.index(a.circling_direction),
                                    order.index(b.circling_direction)))
        return stats

    @property
    def cruise_performance(self):
        from skylines.model.flight_phase import FlightPhase
        return [p for p in self._phases
                if p.aggregate and p.phase_type == FlightPhase.PT_CRUISE]

GeometryDDL(Flight.__table__)
