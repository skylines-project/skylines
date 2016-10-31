# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.types import Integer, Float, String, DateTime
from sqlalchemy.sql.expression import cast
from geoalchemy2.types import Geography, Geometry

from skylines.database import db
from skylines.model.geo import Location


class MountainWaveProject(db.Model):
    __tablename__ = 'mountain_wave_project'

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    location = db.Column(Geometry('POINT', srid=4326))
    axis = db.Column(Geometry('LINESTRING', srid=4326))
    ellipse = db.Column(Geometry('LINESTRING', srid=4326))

    name = db.Column(String())
    country_code = db.Column(String(2))
    vertical = db.Column(Float)
    synoptical = db.Column(String(254))
    main_wind_direction = db.Column(String(254))
    additional = db.Column(String(254))
    source = db.Column(String(254))
    remark1 = db.Column(String(254))
    remark2 = db.Column(String(254))
    orientation = db.Column(Float)
    rotor_height = db.Column(String(254))
    weather_dir = db.Column(Integer)
    axis_length = db.Column(Float)

    def __repr__(self):
        return ('<MountainWaveProject: id=%d name=\'%s\'>' % (self.id, self.name)).encode('unicode_escape')

    @classmethod
    def by_location(cls, location):
        """Returns a query object of mountain waves around the location"""
        if not isinstance(location, Location):
            raise TypeError('Invalid `location` parameter.')

        return cls.query() \
            .filter(db.func.ST_DWithin(
                cast(location.make_point(), Geography),
                cast(cls.location, Geography),
                5000))
