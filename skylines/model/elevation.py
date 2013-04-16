from sqlalchemy import Column
from sqlalchemy.types import Integer
from geoalchemy2.types import Raster

from .base import DeclarativeBase


class Elevation(DeclarativeBase):
    __tablename__ = 'elevations'

    rid = Column(Integer, autoincrement=True, primary_key=True)
    rast = Column(Raster)
