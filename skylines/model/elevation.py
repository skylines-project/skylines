from sqlalchemy import Column
from sqlalchemy.types import Integer
from geoalchemy2.types import Raster

from skylines.model.base import DeclarativeBase
from .session import DBSession


class Elevation(DeclarativeBase):
    __tablename__ = 'elevations'

    rid = Column(Integer, autoincrement=True, primary_key=True)
    rast = Column(Raster)

    @classmethod
    def get(cls, location):
        """
        Returns the elevation at the given location or None.

        location should be WKBElement or WKTElement.
        """

        elevation = cls.rast.ST_Value(location)

        query = DBSession.query(elevation.label('elevation')) \
            .filter(location.ST_Intersects(cls.rast)) \
            .filter(elevation != None)

        return query.scalar()
