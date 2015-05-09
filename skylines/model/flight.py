# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from bisect import bisect_left
from flask import current_app

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import deferred
from sqlalchemy.types import Unicode, Integer, Float, DateTime, Date, \
    Boolean, SmallInteger
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.sql.expression import case, and_, or_, literal_column
from geoalchemy2.types import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import LineString

from skylines.database import db
from skylines.lib.sql import _ST_Intersects, _ST_Contains

from .geo import Location
from .igcfile import IGCFile
from .aircraft_model import AircraftModel
from .elevation import Elevation
from .contest_leg import ContestLeg


class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    pilot_id = db.Column(
        Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)
    pilot = db.relationship('User', foreign_keys=[pilot_id])

    # Fallback if the pilot is not registered
    pilot_name = db.Column(Unicode(255))

    co_pilot_id = db.Column(
        Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)
    co_pilot = db.relationship('User', foreign_keys=[co_pilot_id])

    # Fallback if the co-pilot is not registered
    co_pilot_name = db.Column(Unicode(255))

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
    scoring_start_time = db.Column(DateTime, nullable=True)
    scoring_end_time = db.Column(DateTime, nullable=True)
    landing_time = db.Column(DateTime, nullable=False)

    takeoff_location_wkt = db.Column(
        'takeoff_location', Geometry('POINT', srid=4326))
    landing_location_wkt = db.Column(
        'landing_location', Geometry('POINT', srid=4326))

    takeoff_airport_id = db.Column(
        Integer, db.ForeignKey('airports.id', ondelete='SET NULL'))
    takeoff_airport = db.relationship('Airport', foreign_keys=[takeoff_airport_id])

    landing_airport_id = db.Column(
        Integer, db.ForeignKey('airports.id', ondelete='SET NULL'))
    landing_airport = db.relationship('Airport', foreign_keys=[landing_airport_id])

    timestamps = deferred(db.Column(
        postgresql.ARRAY(DateTime), nullable=False), group='path')

    locations = deferred(db.Column(
        Geometry('LINESTRING', srid=4326), nullable=False),
        group='path')

    olc_classic_distance = db.Column(Integer)
    olc_triangle_distance = db.Column(Integer)
    olc_plus_score = db.Column(Float)

    igc_file_id = db.Column(
        Integer, db.ForeignKey('igc_files.id', ondelete='CASCADE'), nullable=False)
    igc_file = db.relationship('IGCFile', backref='flights', innerjoin=True)

    qnh = db.Column(Float)
    needs_analysis = db.Column(Boolean, nullable=False, default=True)

    # Privacy level of the flight

    class PrivacyLevel:
        PUBLIC = 0
        LINK_ONLY = 1
        PRIVATE = 2

    privacy_level = db.Column(
        SmallInteger, nullable=False, default=PrivacyLevel.PUBLIC)

    ##############################

    def __repr__(self):
        return ('<Flight: id=%s, modified=%s>'
                % (self.id, self.time_modified)).encode('unicode_escape')

    ##############################

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

    # Permissions ################

    @hybrid_method
    def is_viewable(self, user):
        return (self.privacy_level == Flight.PrivacyLevel.PUBLIC or
                self.privacy_level == Flight.PrivacyLevel.LINK_ONLY or
                self.is_writable(user))

    @is_viewable.expression
    def is_viewable_expression(cls, user):
        return or_(cls.privacy_level == Flight.PrivacyLevel.PUBLIC,
                   cls.privacy_level == Flight.PrivacyLevel.LINK_ONLY,
                   cls.is_writable(user))

    @hybrid_method
    def is_listable(self, user):
        return (self.privacy_level == Flight.PrivacyLevel.PUBLIC or
                self.is_writable(user))

    @is_listable.expression
    def is_listable_expression(cls, user):
        return or_(cls.privacy_level == Flight.PrivacyLevel.PUBLIC,
                   cls.is_writable(user))

    @hybrid_method
    def is_rankable(self):
        return self.privacy_level == Flight.PrivacyLevel.PUBLIC

    @hybrid_method
    def is_writable(self, user):
        return user and \
            (self.igc_file.owner_id == user.id or
             self.pilot_id == user.id or
             user.is_manager())

    @is_writable.expression
    def is_writable_expression(self, user):
        return user and (
            user.is_manager() or
            or_(
                IGCFile.owner_id == user.id,
                self.pilot_id == user.id
            )
        )

    @hybrid_method
    def may_delete(self, user):
        return user and (self.igc_file.owner_id == user.id or user.is_manager())

    ##############################

    @classmethod
    def get_largest(cls):
        """Returns a query object ordered by distance"""
        return cls.query().order_by(cls.olc_classic_distance.desc())

    def get_optimised_contest_trace(self, contest_type, trace_type):
        from skylines.model.trace import Trace
        return Trace.query(contest_type=contest_type, trace_type=trace_type,
                           flight=self).first()

    def get_contest_speed(self, contest_type, trace_type):
        contest = self.get_optimised_contest_trace(contest_type, trace_type)
        return contest and contest.speed

    def get_contest_legs(self, contest_type, trace_type):
        return ContestLeg.query(contest_type=contest_type, trace_type=trace_type,
                                flight=self) \
                         .filter(ContestLeg.end_time - ContestLeg.start_time > timedelta(0)) \
                         .order_by(ContestLeg.start_time)

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
        self._phases = []

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
        from skylines.lib.xcsoar_ import flight_path
        from skylines.lib.datetime import from_seconds_of_day

        # Run the IGC file through the FlightPath utility
        path = flight_path(self.igc_file, qnh=self.qnh)
        if len(path) < 2:
            return False

        # Save the timestamps of the coordinates
        date_utc = self.igc_file.date_utc
        self.timestamps = \
            [from_seconds_of_day(date_utc, c.seconds_of_day) for c in path]

        # Convert the coordinate into a list of tuples
        coordinates = [(c.location['longitude'], c.location['latitude']) for c in path]

        # Create a shapely LineString object from the coordinates
        linestring = LineString(coordinates)

        # Save the new path as WKB
        self.locations = from_shape(linestring, srid=4326)

        return True


class FlightPathChunks(db.Model):
    """
    This table stores flight path chunks of about 100 fixes per column which
    enable PostGIS/Postgres to do fast queries due to tight bounding boxes
    around those short flight pahts.
    """

    __tablename__ = 'flight_path_chunks'

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    timestamps = deferred(db.Column(
        postgresql.ARRAY(DateTime), nullable=False), group='path')

    locations = deferred(db.Column(
        Geometry('LINESTRING', srid=4326), nullable=False),
        group='path')

    start_time = db.Column(DateTime, nullable=False, index=True)
    end_time = db.Column(DateTime, nullable=False, index=True)

    flight_id = db.Column(
        Integer, db.ForeignKey('flights.id', ondelete='CASCADE'), nullable=False,
        index=True)
    flight = db.relationship('Flight')

    @staticmethod
    def get_near_flights(flight, filter=None):
        """
        WITH src AS
            (SELECT ST_Buffer(ST_Simplify(locations, 0.005), 0.015) AS src_loc_buf,
                    start_time AS src_start,
                    end_time AS src_end
             FROM flight_paths
             WHERE flight_id = 8503)
        SELECT (dst_points).geom AS dst_point,
               dst_times[(dst_points).path[1]] AS dst_time,
               dst_points_fid AS dst_flight_id
        FROM
            (SELECT ST_dumppoints(locations) as dst_points,
                    timestamps AS dst_times,
                    src_loc_buf,
                    flight_id AS dst_points_fid,
                    src_start,
                    src_end
            FROM flight_paths, src
            WHERE flight_id != 8503 AND
                  end_time >= src_start AND
                  start_time <= src_end AND
                  locations && src_loc_buf AND
                  _ST_Intersects(ST_Simplify(locations, 0.005), src_loc_buf)) AS foo
        WHERE _ST_Contains(src_loc_buf, (dst_points).geom);
        """

        cte = db.session.query(FlightPathChunks.locations.ST_Simplify(0.005).ST_Buffer(0.015).label('src_loc_buf'),
                               FlightPathChunks.start_time.label('src_start'),
                               FlightPathChunks.end_time.label('src_end')) \
            .filter(FlightPathChunks.flight == flight) \
            .cte('src')

        subq = db.session.query(func.ST_DumpPoints(FlightPathChunks.locations).label('dst_points'),
                                FlightPathChunks.timestamps.label('dst_times'),
                                cte.c.src_loc_buf,
                                FlightPathChunks.flight_id.label('dst_points_fid'),
                                cte.c.src_start,
                                cte.c.src_end) \
            .filter(and_(FlightPathChunks.flight != flight,
                         FlightPathChunks.end_time >= cte.c.src_start,
                         FlightPathChunks.start_time <= cte.c.src_end,
                         FlightPathChunks.locations.intersects(cte.c.src_loc_buf),
                         _ST_Intersects(FlightPathChunks.locations.ST_Simplify(0.005), cte.c.src_loc_buf))) \
            .subquery()

        dst_times = literal_column('dst_times[(dst_points).path[1]]')

        q = db.session.query(subq.c.dst_points.geom.label('dst_location'),
                             dst_times.label('dst_time'),
                             subq.c.dst_points_fid.label('dst_point_fid')) \
            .filter(_ST_Contains(subq.c.src_loc_buf, subq.c.dst_points.geom)) \
            .order_by(subq.c.dst_points_fid, dst_times) \
            .all()

        src_trace = to_shape(flight.locations).coords
        max_distance = 1000
        other_flights = dict()

        for point in q:
            dst_time = point.dst_time
            dst_loc = to_shape(point.dst_location).coords

            # we might have got a destination point earier than source takeoff
            # or later than source landing. Check this case and disregard early.
            if dst_time < flight.takeoff_time or dst_time > flight.landing_time:
                continue

            # find point closest to given time
            closest = bisect_left(flight.timestamps, dst_time, hi=len(flight.timestamps) - 1)

            if closest == 0:
                src_point = src_trace[0]
            else:
                # interpolate flight trace between two fixes
                dx = (dst_time - flight.timestamps[closest - 1]).total_seconds() / \
                     (flight.timestamps[closest] - flight.timestamps[closest - 1]).total_seconds()

                src_point_prev = src_trace[closest - 1]
                src_point_next = src_trace[closest]

                src_point = [src_point_prev[0] + (src_point_next[0] - src_point_prev[0]) * dx,
                             src_point_prev[1] + (src_point_next[1] - src_point_prev[1]) * dx]

            point_distance = Location(latitude=dst_loc[0][1], longitude=dst_loc[0][0]).geographic_distance(
                Location(latitude=src_point[1], longitude=src_point[0]))

            if point_distance > max_distance:
                continue

            if point.dst_point_fid not in other_flights:
                other_flights[point.dst_point_fid] = []
                other_flights[point.dst_point_fid].append(dict(times=list(), points=list()))

            elif len(other_flights[point.dst_point_fid][-1]['times']) and \
                    (dst_time - other_flights[point.dst_point_fid][-1]['times'][-1]).total_seconds() > 600:
                other_flights[point.dst_point_fid].append(dict(times=list(), points=list()))

            other_flights[point.dst_point_fid][-1]['times'].append(dst_time)
            other_flights[point.dst_point_fid][-1]['points'].append(Location(latitude=dst_loc[0][1], longitude=dst_loc[0][0]))

        return other_flights

    @staticmethod
    def update_flight_path(flight):
        from skylines.lib.xcsoar_ import flight_path
        from skylines.lib.datetime import from_seconds_of_day

        # Now populate the FlightPathChunks table with the (full) flight path
        path_detailed = flight_path(flight.igc_file, max_points=3000, qnh=flight.qnh)
        if len(path_detailed) < 2:
            return False

        # Number of points in each chunck.
        num_points = 100

        # Interval of the current chunck: [i, j] (-> path_detailed[i:j + 1])
        i = 0
        j = min(num_points - 1, len(path_detailed) - 1)

        # Ensure that the last chunk contains at least two fixes
        if j == len(path_detailed) - 2:
            j = len(path_detailed) - 1

        FlightPathChunks.query().filter(FlightPathChunks.flight == flight).delete()
        date_utc = flight.igc_file.date_utc

        while True:
            flight_path = FlightPathChunks(flight=flight)

            # Save the timestamps of the coordinates
            flight_path.timestamps = \
                [from_seconds_of_day(date_utc, c.seconds_of_day) for c in path_detailed[i:j + 1]]

            flight_path.start_time = path_detailed[i].datetime
            flight_path.end_time = path_detailed[j].datetime

            # Convert the coordinate into a list of tuples
            coordinates = [(c.location['longitude'], c.location['latitude']) for c in path_detailed[i:j + 1]]

            # Create a shapely LineString object from the coordinates
            linestring = LineString(coordinates)

            # Save the new path as WKB
            flight_path.locations = from_shape(linestring, srid=4326)

            db.session.add(flight_path)

            if j == len(path_detailed) - 1:
                break
            else:
                i = j + 1
                j = min(j + num_points, len(path_detailed) - 1)

                if j == len(path_detailed) - 2:
                    j = len(path_detailed) - 1

        db.session.commit()

        return True


def get_elevations_for_flight(flight):
    cached_elevations = current_app.cache.get('elevations_' + flight.__repr__())
    if cached_elevations:
        return cached_elevations

    '''
    WITH src AS
        (SELECT ST_DumpPoints(flights.locations) AS location,
                flights.timestamps AS timestamps,
                flights.locations AS locations
        FROM flights
        WHERE flights.id = 30000)
    SELECT timestamps[(src.location).path[1]] AS timestamp,
           ST_Value(elevations.rast, (src.location).geom) AS elevation
    FROM elevations, src
    WHERE src.locations && elevations.rast AND (src.location).geom && elevations.rast;
    '''

    # Prepare column expressions
    location = Flight.locations.ST_DumpPoints()

    # Prepare cte
    cte = db.session.query(location.label('location'),
                           Flight.locations.label('locations'),
                           Flight.timestamps.label('timestamps')) \
                    .filter(Flight.id == flight.id).cte()

    # Prepare column expressions
    timestamp = literal_column('timestamps[(location).path[1]]')
    elevation = Elevation.rast.ST_Value(cte.c.location.geom)

    # Prepare main query
    q = db.session.query(timestamp.label('timestamp'),
                         elevation.label('elevation')) \
                  .filter(and_(cte.c.locations.intersects(Elevation.rast),
                               cte.c.location.geom.intersects(Elevation.rast))).all()

    if len(q) == 0:
        return []

    start_time = q[0][0]
    start_midnight = start_time.replace(hour=0, minute=0, second=0,
                                        microsecond=0)

    elevations = []
    for time, elevation in q:
        if elevation is None:
            continue

        time_delta = time - start_midnight
        time = time_delta.days * 86400 + time_delta.seconds

        elevations.append((time, elevation))

    current_app.cache.set('elevations_' + flight.__repr__(), elevations, timeout=3600 * 24)

    return elevations
