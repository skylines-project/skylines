from pytz import timezone
from sqlalchemy.types import Integer, String
from geoalchemy2.types import Geometry

from skylines.database import db


class TimeZone(db.Model):
    __tablename__ = 'tz_world'

    id = db.Column('gid', Integer, autoincrement=True, primary_key=True)
    tzid = db.Column(String(30))
    the_geom = db.Column(Geometry('MULTIPOLYGON', srid=4326))

    def __unicode__(self):
        return self.tzid

    def __repr__(self):
        return ('<TimeZone: id=%d tzid=\'%s\'>' % (self.id, self.tzid)).encode('unicode_escape')

    @classmethod
    def by_location(cls, location):
        location = location.make_point(srid=None)
        filter = db.func.ST_Contains(cls.the_geom, location)
        zone = db.session.query(cls.tzid).filter(filter).scalar()
        if zone is None:
            return None

        return timezone(unicode(zone))
