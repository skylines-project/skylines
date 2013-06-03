from pytz import timezone
from sqlalchemy import Column
from sqlalchemy.types import Integer, String
from sqlalchemy.sql.expression import func
from geoalchemy2.types import Geometry

from skylines import db


class TimeZone(db.Model):
    __tablename__ = 'tz_world'

    id = Column('gid', Integer, autoincrement=True, primary_key=True)
    tzid = Column(String(30))
    the_geom = Column(Geometry('MULTIPOLYGON'))

    def __unicode__(self):
        return self.tzid

    def __repr__(self):
        return ('<AircraftModel: id=%d tzid=\'%s\'>' % (self.id, self.tzid)).encode('utf-8')

    @classmethod
    def by_location(cls, location):
        location = func.ST_MakePoint(location.longitude, location.latitude)
        filter = func.ST_Contains(cls.the_geom, location)
        zone = db.session.query(cls.tzid).filter(filter).scalar()
        if zone is None:
            return None

        return timezone(unicode(zone))
