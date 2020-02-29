from datetime import datetime, timedelta
from bisect import bisect_left

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import deferred
from sqlalchemy.types import (
    Unicode,
    Integer,
    String,
    Float,
    DateTime,
    Date,
    Boolean,
    SmallInteger,
)
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.sql.expression import case, and_, or_, literal_column
from geoalchemy2.types import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import LineString

from skylines.database import db
from skylines.lib.sql import _ST_Intersects, _ST_Contains
from skylines.lib.string import unicode_to_str

from .geo import Location
from .igcfile import IGCFile
from .aircraft_model import AircraftModel
from .contest_leg import ContestLeg

class Groupflight(db.Model):
    __tablename__ = "groupflights"

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    club_id = db.Column(Integer, db.ForeignKey("clubs.id"), index=True)
    club = db.relationship("Club", backref="groupflights")
    flight_plan_md5 = db.Column(String(32), nullable=False)
    landscape = db.Column(String(32), nullable=False)
    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    date_flight = db.Column(DateTime, nullable=False, default=datetime.utcnow().date())
    takeoff_airport_id = db.Column(Integer, db.ForeignKey("airports.id"))
    takeoff_airport = db.relationship("Airport", foreign_keys=[takeoff_airport_id])



