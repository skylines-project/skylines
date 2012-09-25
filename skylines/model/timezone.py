from sqlalchemy import Column
from sqlalchemy.types import Integer, String
from skylines.model.base import DeclarativeBase
from skylines.model.session import DBSession
from geoalchemy.geometry import GeometryColumn, GeometryDDL, MultiPolygon
from geoalchemy.postgis import PGComparator
from geoalchemy.functions import functions
from sqlalchemy.sql.expression import func
from pytz import timezone


class TimeZone(DeclarativeBase):
    __tablename__ = 'tz_world'

    id = Column('gid', Integer, autoincrement=True, primary_key=True)
    tzid = Column(String(30))
    the_geom = GeometryColumn(MultiPolygon, comparator=PGComparator)

    def __unicode__(self):
        return self.tzid

    @classmethod
    def by_location(cls, location):
        location = func.ST_MakePoint(location.longitude, location.latitude)
        filter = functions.gcontains(cls.the_geom, location)
        zone = DBSession.query(cls.tzid).filter(filter).scalar()
        if zone is None:
            return None

        return timezone(unicode(zone))

GeometryDDL(TimeZone.__table__)
