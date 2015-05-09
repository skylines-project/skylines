from sqlalchemy.types import Integer
from geoalchemy2.types import Raster

from skylines.database import db


class Elevation(db.Model):
    __tablename__ = 'elevations'

    rid = db.Column(Integer, autoincrement=True, primary_key=True)
    rast = db.Column(Raster)

    @classmethod
    def get(cls, location):
        """
        Returns the elevation at the given location or None.

        location should be WKBElement or WKTElement.
        """

        elevation = cls.rast.ST_Value(location)

        query = db.session.query(elevation.label('elevation')) \
            .filter(location.ST_Intersects(cls.rast)) \
            .filter(elevation != None)

        return query.scalar()
