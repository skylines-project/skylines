# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from sqlalchemy.types import Integer, REAL, DateTime, SmallInteger, Unicode, BigInteger
from sqlalchemy.dialects.postgresql import INET
from geoalchemy2.types import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point

from skylines.database import db
from skylines.lib.types import is_int
from skylines.lib.string import unicode_to_str
from .geo import Location


class TrackingFix(db.Model):
    __tablename__ = "tracking_fixes"

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    time = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_visible = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    location_wkt = db.Column("location", Geometry("POINT", srid=4326))

    track = db.Column(SmallInteger)
    ground_speed = db.Column(REAL)
    airspeed = db.Column(REAL)
    altitude = db.Column(SmallInteger)
    elevation = db.Column(SmallInteger)
    vario = db.Column(REAL)
    engine_noise_level = db.Column(SmallInteger)

    pilot_id = db.Column(
        Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pilot = db.relationship("User", innerjoin=True)

    ip = db.Column(INET)

    def __repr__(self):
        return unicode_to_str(
            "<TrackingFix: id={} time='{}'>".format(self.id, self.time)
        )

    @property
    def location(self):
        if self.location_wkt is None:
            return None

        coords = to_shape(self.location_wkt)
        return Location(latitude=coords.y, longitude=coords.x)

    def set_location(self, longitude, latitude):
        self.location_wkt = from_shape(Point(longitude, latitude), srid=4326)

    @property
    def altitude_agl(self):
        if not self.elevation:
            raise ValueError("This TrackingFix has no elevation.")

        return max(0, self.altitude - self.elevation)

    @classmethod
    def max_age_filter(cls, max_age):
        """
        Returns a filter that makes sure that the fix is not older than a
        certain time.

        The delay parameter can be either a datetime.timedelta or a numeric
        value that will be interpreted as hours.
        """

        if is_int(max_age) or isinstance(max_age, float):
            max_age = timedelta(hours=max_age)

        return cls.time >= datetime.utcnow() - max_age

    @classmethod
    def get_latest(cls, max_age=timedelta(hours=6)):
        # Add a db.Column to the inner query with
        # numbers ordered by time for each pilot
        row_number = db.over(
            db.func.row_number(), partition_by=cls.pilot_id, order_by=cls.time.desc()
        )

        # Create inner query
        subq = (
            db.session.query(cls.id, row_number.label("row_number"))
            .join(cls.pilot)
            .filter(cls.max_age_filter(max_age))
            .filter(cls.time_visible <= datetime.utcnow())
            .filter(cls.location_wkt != None)
            .subquery()
        )

        # Create outer query that orders by time and
        # only selects the latest fix
        query = (
            cls.query()
            .options(db.joinedload(cls.pilot))
            .filter(cls.id == subq.c.id)
            .filter(subq.c.row_number == 1)
            .order_by(cls.time.desc())
        )

        return query


db.Index("tracking_fixes_pilot_time", TrackingFix.pilot_id, TrackingFix.time)


class TrackingSession(db.Model):
    __tablename__ = "tracking_sessions"

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    pilot_id = db.Column(
        Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    pilot = db.relationship("User", innerjoin=True)

    lt24_id = db.Column(BigInteger, index=True)

    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    ip_created = db.Column(INET)

    time_finished = db.Column(DateTime)
    ip_finished = db.Column(INET)

    # client application
    client = db.Column(Unicode(32))
    client_version = db.Column(Unicode(8))

    # device information
    device = db.Column(Unicode(32))
    gps_device = db.Column(Unicode(32))

    # aircraft information
    aircraft_type = db.Column(SmallInteger)
    aircraft_model = db.Column(Unicode(64))

    # status of the pilot after landing
    #
    # 0-> "Everything OK"
    # 1-> "Need retrieve"
    # 2-> "Need some help, nothing broken"
    # 3-> "Need help, maybe something broken"
    # 4-> "HELP, SERIOUS INJURY"
    finish_status = db.Column(SmallInteger)

    def __repr__(self):
        return unicode_to_str("<TrackingSession: id={}>".format(self.id))

    @classmethod
    def by_lt24_id(cls, lt24_id, filter_finished=True):
        query = cls.query(lt24_id=lt24_id)

        if filter_finished:
            query = query.filter_by(time_finished=None)

        return query.order_by(cls.time_created.desc()).first()
