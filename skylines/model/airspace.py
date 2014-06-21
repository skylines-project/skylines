# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.types import Integer, String, DateTime
from geoalchemy2.types import Geometry

from skylines.model import db


class Airspace(db.Model):
    __tablename__ = 'airspace'

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    the_geom = db.Column(Geometry('POLYGON', srid=4326))

    name = db.Column(String(), nullable=False)
    airspace_class = db.Column(String(3), nullable=False)
    base = db.Column(String(30), nullable=False)
    top = db.Column(String(30), nullable=False)
    country_code = db.Column(String(2), nullable=False)

    def __repr__(self):
        return ('<Airspace: id=%d name=\'%s\'>' % (self.id, self.name)).encode('unicode_escape')

    @classmethod
    def by_location(cls, location):
        '''Returns a query object of all airspaces at the location'''
        return cls.query() \
            .filter(cls.the_geom.ST_Contains(location.make_point()))

    def extract_height(self, column):
        if column == 'GND':
            return -1000, 'msl'

        elif column.startswith('FL'):
            return int(column[3:]) * 100 / 3.2808399, 'fl'

        elif column.endswith('AGL'):
            return int(column[:-4]) / 3.2808399, 'agl'

        elif column.endswith('MSL'):
            return int(column[:-4]) / 3.2808399, 'msl'

        elif column == 'NOTAM':
            return -1000, 'notam'

        else:
            return -1000, 'unknown'

    @property
    def extract_base(self):
        return self.extract_height(self.base)

    @property
    def extract_top(self):
        return self.extract_height(self.top)
