from pytz import timezone
from sqlalchemy import Column
from sqlalchemy.types import Integer, String
from sqlalchemy.sql.expression import func
from geoalchemy2.types import Geometry

from .base import DeclarativeBase
from .session import DBSession


class TimeZone(DeclarativeBase):
    __tablename__ = 'tz_world'

    id = Column('gid', Integer, autoincrement=True, primary_key=True)
    tzid = Column(String(30))
    the_geom = Column(Geometry('MULTIPOLYGON', management=True))

    def __unicode__(self):
        return self.tzid

    def __repr__(self):
        return ('<AircraftModel: id=%d tzid=\'%s\'>' % (self.id, self.tzid)).encode('utf-8')

    @classmethod
    def by_location(cls, location):
        location = func.ST_MakePoint(location.longitude, location.latitude)
        filter = func.ST_Contains(cls.the_geom, location)
        zone = DBSession.query(cls.tzid).filter(filter).scalar()
        if zone is None:
            return None

        return timezone(unicode(zone))
