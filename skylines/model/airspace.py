# -*- coding: utf-8 -*-

from datetime import datetime
from itertools import groupby, count

from sqlalchemy.types import Integer, String, DateTime
from geoalchemy2.types import Geometry
from geoalchemy2.shape import from_shape
from shapely.geometry import LineString

from skylines.model import db
from skylines.lib.sql import _ST_Contains
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

    # Save the new path as WKB
    locations = from_shape(linestring, srid=4326)

    airspaces_q = db.session.query(Airspace) \
                    .filter(Airspace.the_geom.ST_Intersects(locations))

    airspaces_cte = airspaces_q.cte()
    cte = db.session.query(locations.ST_DumpPoints().label('locations')).cte()

    q = db.session.query(airspaces_cte.c.id,
                         cte.c.locations.path[1]) \
                  .filter(_ST_Contains(airspaces_cte.c.the_geom, cte.c.locations.geom))

    airspaces = dict()

    for airspace in airspaces_q.all():
        top, top_ref = airspace.extract_top
        base, base_ref = airspace.extract_base

        airspaces[airspace.id] = dict(
            airspace_class=airspace.airspace_class,
            top=top,
            top_ref=top_ref,
            top_text=airspace.top,
            base=base,
            base_ref=base_ref,
            base_text=airspace.base,
            name=airspace.name)

    infringements = set()
    periods_dict = dict()

    for as_id, i in q.all():
        fix_id = i - 1

        # TODO: respect airspace height references (MSL, AGL, FL)
        if flight_path[fix_id].gps_altitude <= airspaces[as_id]['top'] and \
           flight_path[fix_id].gps_altitude >= airspaces[as_id]['base']:
            infringements.add(as_id)

            if as_id not in periods_dict:
                periods_dict[as_id] = []

            periods_dict[as_id].append(fix_id)

    periods = []
    for as_id in periods_dict:
        periods_dict[as_id].sort()
        for k, g in groupby(periods_dict[as_id], key=lambda n, c=count(): n - next(c)):
            g = list(g)
            periods.append((as_id, g[0], g[-1]))

    return airspaces, infringements, periods
