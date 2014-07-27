# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.types import Integer, String, DateTime
from geoalchemy2.types import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import LineString, box
import xcsoar

from skylines.model import db
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
        '''Returns a query object of all airspaces at the location'''
        return cls.query() \
            .filter(cls.the_geom.ST_Contains(location.make_point()))

    def extract_height(self, column):
        if column == 'GND':
            return -1000, 'msl'

        elif column.startswith('FL'):
            return float(column[3:]) * 100 / FEET_PER_METER, 'fl'

        elif column.endswith('AGL'):
            return float(column[:-4]) / FEET_PER_METER, 'agl'

        elif column.endswith('MSL'):
            return float(column[:-4]) / FEET_PER_METER, 'msl'

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


def get_airspace_infringements(flight_path):
    # Convert the coordinate into a list of tuples
    coordinates = [(c.location['longitude'], c.location['latitude']) for c in flight_path]

    # Create a shapely LineString object from the coordinates
    linestring = LineString(coordinates)

    bbox = from_shape(box(*linestring.bounds), srid=4326)

    q = db.session.query(Airspace) \
          .filter(Airspace.the_geom.intersects(bbox))

    xcs_airspace = xcsoar.Airspaces()

    for airspace in q.all():
        poly = list(to_shape(airspace.the_geom).exterior.coords)
        coords = [dict(latitude=c[1], longitude=c[0]) for c in poly]

        top, top_ref = airspace.extract_top
        base, base_ref = airspace.extract_base

        xcs_airspace.addPolygon(coords, str(airspace.id), airspace.airspace_class,
                                base * 3.2808399, base_ref.upper(),
                                top * 3.2808399, top_ref.upper())

    xcs_airspace.optimise()
    xcs_flight = xcsoar.Flight(flight_path)
    infringements = xcs_airspace.findIntrusions(xcs_flight)

    # Replace airspace id string with ints in returned infringements
    return dict((int(k), v) for k, v in infringements.items())
