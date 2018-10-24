from pytz import timezone
from sqlalchemy.types import Integer, String
from geoalchemy2.types import Geometry

from skylines.database import db
from skylines.lib.string import unicode_to_str


# Instructions
#
# - download raw data from http://efele.net/maps/tz/world/tz_world.zip
# - shp2pgsql -D -s 4326 tz_world.shp > dump.sql
# - psql skylines -f dump.sql


class TimeZone(db.Model):
    __tablename__ = "tz_world"

    id = db.Column("gid", Integer, autoincrement=True, primary_key=True)
    tzid = db.Column(String(30))
    the_geom = db.Column(Geometry("MULTIPOLYGON", srid=4326))

    def __unicode__(self):
        return self.tzid

    def __repr__(self):
        return unicode_to_str("<TimeZone: tzid='%s'>" % (self.tzid))

    @classmethod
    def by_location(cls, location):
        location = location.make_point()
        filter = db.func.ST_Contains(cls.the_geom, location)
        zone = db.session.query(cls.tzid).filter(filter).scalar()
        if zone is None:
            return None

        return timezone(zone)
