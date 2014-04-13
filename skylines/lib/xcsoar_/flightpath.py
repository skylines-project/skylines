from collections import namedtuple
from sqlalchemy.sql.expression import and_, literal_column
from shapely.geometry import MultiPoint
from geoalchemy2.shape import from_shape

from skylines.lib import files
from skylines.lib.sql import extract_array_item
from skylines.model import db, Elevation, IGCFile
from xcsoar import Flight


flightpathfix_fields = ['datetime', 'seconds_of_day',
                        'location', 'altitude', 'pressure_altitude',
                        'enl', 'track', 'groundspeed', 'tas', 'ias',
                        'siu', 'elevation']


class FlightPathFix(namedtuple('FlightPathFix', flightpathfix_fields)):
    def __new__(cls, *args, **kwargs):
        values = [None] * 12

        values[:min(12, len(args))] = args[:12]

        for i, key in enumerate(flightpathfix_fields):
            if key in kwargs:
                values[i] = kwargs[key]

        return super(FlightPathFix, cls).__new__(cls, *values)


def run_flight_path(path, max_points=None):
    flight = Flight(path)

    if max_points:
        flight.reduce(max_points=max_points)

    return flight.path()


def flight_path(igc_file, max_points=1000, add_elevation=False):
    if isinstance(igc_file, IGCFile):
        path = files.filename_to_path(igc_file.filename)
    elif isinstance(igc_file, (str, unicode)):
        path = igc_file
    else:
        return None

    output = run_flight_path(path, max_points=max_points)

    if add_elevation:
        output = get_elevation(output)

    return map(lambda line: FlightPathFix(*line), output)


def get_elevation(fixes):
    shortener = int(max(1, len(fixes) / 1000))

    coordinates = [(fix[2]['longitude'], fix[2]['latitude']) for fix in fixes]
    points = MultiPoint(coordinates[::shortener])
    locations = from_shape(points, srid=4326).ST_DumpPoints()
    locations_id = extract_array_item(locations.path, 1)

    subq = db.session.query(locations_id.label('location_id'),
                            locations.geom.label('location')).subquery()

    elevation = Elevation.rast.ST_Value(subq.c.location)

    # Prepare main query
    q = db.session.query(literal_column('location_id'), elevation.label('elevation')) \
                  .filter(and_(subq.c.location.ST_Intersects(Elevation.rast),
                               elevation != None)).all()

    fixes_copy = [list(fix) for fix in fixes]

    for i in xrange(1, len(q)):
        prev = q[i - 1].location_id - 1
        current = q[i].location_id - 1

        for j in range(prev * shortener, current * shortener):
            elev = q[i - 1].elevation + (q[i].elevation - q[i - 1].elevation) * (j - prev * shortener)
            fixes_copy[j][11] = elev

    if len(q):
        fixes_copy[-1][11] = q[-1].elevation

    return fixes_copy
