# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.types import Integer, String, DateTime
from geoalchemy2.types import Geometry

from skylines.model import db


class Boundaries(db.Model):
    __tablename__ = 'boundaries'

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    geometry = db.Column(Geometry('MULTIPOLYGON', srid=4326))

    name = db.Column(String())
    name_long = db.Column(String())
    abbrev = db.Column(String())
    iso_a2 = db.Column(String(2))
    iso_a3 = db.Column(String(3))
    region = db.Column(String())
    subregion = db.Column(String())
    continent = db.Column(String())

    def __repr__(self):
        return ('<Boundaries: id=%d name=\'%s\'>' % (self.id, self.name)).encode('unicode_escape')
