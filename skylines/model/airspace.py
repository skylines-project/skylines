# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.types import Integer, String, DateTime
from geoalchemy2.types import Geometry
from geoalchemy2.elements import WKTElement

from skylines import db


class Airspace(db.Model):
    __tablename__ = 'airspace'

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    the_geom = db.Column(Geometry('POLYGON'))

    name = db.Column(String(), nullable=False)
    airspace_class = db.Column(String(3), nullable=False)
    base = db.Column(String(30), nullable=False)
    top = db.Column(String(30), nullable=False)
    country_code = db.Column(String(2), nullable=False)

    def __repr__(self):
        return ('<Airspace: id=%d name=\'%s\'>' % (self.id, self.name)).encode('unicode_escape')

    @classmethod
    def get_info(cls, location):
        '''Returns a query object of all airspaces at the location'''
        return cls.query() \
            .filter(cls.the_geom.ST_Contains(WKTElement(location.to_wkt(), srid=4326)))
