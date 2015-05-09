# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.types import Integer, String, DateTime
from geoalchemy2.types import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import LineString, box
import xcsoar

from flask import current_app

from skylines.database import db
from skylines.lib.geo import FEET_PER_METER


class Airspace(db.Model):
    __tablename__ = 'airspace'

    id = db.Column(Integer, autoincrement=True, primary_key=True)
    time_created = db.Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    the_geom = db.Column(Geometry('POLYGON', srid=4326))

    name = db.Column(String(), nullable=False)
    airspace_class = db.Column(String(12), nullable=False)
    base = db.Column(String(30), nullable=False)
    top = db.Column(String(30), nullable=False)
    country_code = db.Column(String(2), nullable=False)

    def __repr__(self):
        return ('<Airspace: id=%d name=\'%s\'>' % (self.id, self.name)).encode('unicode_escape')

    @classmethod
    def by_location(cls, location):
        """Returns a query object of all airspaces at the location"""
        return cls.query() \
            .filter(cls.the_geom.ST_Contains(location.make_point()))

    def extract_height(self, column):
        if column == 'GND':
            return -1000, 'MSL'

        elif column.startswith('FL'):
            return float(column[3:]) * 100 / FEET_PER_METER, 'FL'

        elif column.endswith('AGL'):
            return float(column[:-4]) / FEET_PER_METER, 'AGL'

        elif column.endswith('MSL'):
            return float(column[:-4]) / FEET_PER_METER, 'MSL'

        elif column == 'NOTAM':
            return -1000, 'NOTAM'

        else:
            return -1000, 'UNKNOWN'

    @property
    def extract_base(self):
        return self.extract_height(self.base)

    @property
    def extract_top(self):
        return self.extract_height(self.top)


def get_airspace_infringements(flight_path, qnh=None):
    # Convert the coordinate into a list of tuples
    coordinates = [(c.location['longitude'], c.location['latitude']) for c in flight_path]

    # Create a shapely LineString object from the coordinates
    linestring = LineString(coordinates)

    bbox = from_shape(box(*linestring.bounds), srid=4326)

    q = db.session.query(Airspace) \
          .filter(Airspace.the_geom.intersects(bbox))

    xcs_airspace = xcsoar.Airspaces()

    for airspace in q.all():
        if airspace.airspace_class not in current_app.config['SKYLINES_AIRSPACE_CHECK']:
            continue

        poly = list(to_shape(airspace.the_geom).exterior.coords)
        coords = [dict(latitude=c[1], longitude=c[0]) for c in poly]

        top, top_ref = airspace.extract_top
        base, base_ref = airspace.extract_base

        if top_ref == 'NOTAM' or top_ref == 'UNKNOWN':
            top_ref = 'MSL'

        if base_ref == 'NOTAM' or base_ref == 'UNKNOWN':
            base_ref = 'MSL'

        xcs_airspace.addPolygon(coords, str(airspace.id), airspace.airspace_class,
                                base, base_ref.upper(),
                                top, top_ref.upper())

    xcs_airspace.optimise()
    xcs_flight = xcsoar.Flight(flight_path)

    if qnh:
        xcs_flight.setQNH(qnh)

    infringements = xcs_airspace.findIntrusions(xcs_flight)

    # Replace airspace id string with ints in returned infringements
    return dict((int(k), v) for k, v in infringements.items())
