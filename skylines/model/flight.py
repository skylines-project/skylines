# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.dialects import postgresql
from sqlalchemy.types import Unicode, Integer, DateTime, Date, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import case
from geoalchemy2.types import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import LineString

from skylines import db
from .geo import Location
from .igcfile import IGCFile
from .aircraft_model import AircraftModel


class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    pilot_id = db.Column(
        Integer, db.ForeignKey('tg_user.id', ondelete='SET NULL'), index=True)
    pilot = db.relationship('User', foreign_keys=[pilot_id])

    co_pilot_id = db.Column(
        Integer, db.ForeignKey('tg_user.id', ondelete='SET NULL'), index=True)
    co_pilot = db.relationship('User', foreign_keys=[co_pilot_id])

    club_id = db.Column(
        Integer, db.ForeignKey('clubs.id', ondelete='SET NULL'), index=True)
    club = db.relationship('Club', backref='flights')

    model_id = db.Column(Integer, db.ForeignKey('models.id', ondelete='SET NULL'))
    model = db.relationship('AircraftModel')
    registration = db.Column(Unicode(32))
    competition_id = db.Column(Unicode(5))

    # The date of the flight in local time instead of UTC. Used for scoring.
    date_local = db.Column(Date, nullable=False, index=True)

    takeoff_time = db.Column(DateTime, nullable=False, index=True)
    landing_time = db.Column(DateTime, nullable=False)
    takeoff_location_wkt = db.Column(
        'takeoff_location', Geometry('POINT'))
    landing_location_wkt = db.Column(
        'landing_location', Geometry('POINT'))

    takeoff_airport_id = db.Column(
        Integer, db.ForeignKey('airports.id', ondelete='SET NULL'))
    takeoff_airport = db.relationship('Airport', foreign_keys=[takeoff_airport_id])

    landing_airport_id = db.Column(
        Integer, db.ForeignKey('airports.id', ondelete='SET NULL'))
    landing_airport = db.relationship('Airport', foreign_keys=[landing_airport_id])

    timestamps = db.Column(postgresql.ARRAY(DateTime), nullable=False)
    locations = db.Column(
        Geometry('LINESTRING', srid=4326), nullable=False)

    olc_classic_distance = db.Column(Integer)
    olc_triangle_distance = db.Column(Integer)
    olc_plus_score = db.Column(Integer)

    igc_file_id = db.Column(
        Integer, db.ForeignKey('igc_files.id', ondelete='CASCADE'), nullable=False)
    igc_file = db.relationship('IGCFile', backref='flights', innerjoin=True)

    needs_analysis = db.Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return ('<Flight: id=%d>' % self.id).encode('unicode_escape')

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
        return case([(AircraftModel.dmst_index > 0, cls.olc_plus_score * 100 / AircraftModel.dmst_index)], else_=cls.olc_plus_score)

    @year.expression
    def year(cls):
        return db.func.date_part('year', cls.date_local)

    @property
    def takeoff_location(self):
        if self.takeoff_location_wkt is None:
            return None

        coords = to_shape(self.takeoff_location_wkt)
        return Location(latitude=coords.y, longitude=coords.x)

    @takeoff_location.setter
    def takeoff_location(self, location):
        if location is None:
            self.takeoff_location_wkt = None
        else:
            self.takeoff_location_wkt = location.to_wkt_element()

    @property
    def landing_location(self):
        if self.landing_location_wkt is None:
            return None

        coords = to_shape(self.landing_location_wkt)
        return Location(latitude=coords.y, longitude=coords.x)

    @landing_location.setter
    def landing_location(self, location):
        if location is None:
            self.landing_location_wkt = None
        else:
            self.landing_location_wkt = location.to_wkt_element()

    @classmethod
    def by_md5(cls, _md5):
        file = IGCFile.by_md5(_md5)
        if file is None:
            return None

        return cls.query().filter_by(igc_file=file).first()

    def is_writable(self, user):
        return user and \
            (self.igc_file.owner_id == user.id or
             self.pilot_id == user.id or
             user.is_manager())

    def may_delete(self, user):
        return user and (self.igc_file.owner_id == user.id or user.is_manager())

    @classmethod
    def get_largest(cls):
        '''Returns a query object ordered by distance'''
        return cls.query().order_by(cls.olc_classic_distance.desc())

    def get_optimised_contest_trace(self, contest_type, trace_type):
        from skylines.model.trace import Trace
        return Trace.query(contest_type=contest_type, trace_type=trace_type,
                           flight=self).first()

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
        FlightPhase.query(flight=self).delete()

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

    def update_flight_path(self):
        from skylines.lib.xcsoar import flight_path
        from skylines.lib.datetime import from_seconds_of_day

        # Run the IGC file through the FlightPath utility
        path = flight_path(self.igc_file)
        if len(path) < 2:
            return False

        # Save the timestamps of the coordinates
        date_utc = self.igc_file.date_utc
        self.timestamps = \
            [from_seconds_of_day(date_utc, c.seconds_of_day) for c in path]

        # Convert the coordinate into a list of tuples
        coordinates = [(c.longitude, c.latitude) for c in path]

        # Create a shapely LineString object from the coordinates
        linestring = LineString(coordinates)

        # Save the new path as WKB
        self.locations = from_shape(linestring, srid=4326)

        return True
