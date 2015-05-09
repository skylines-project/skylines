from collections import namedtuple
from sqlalchemy.sql.expression import and_, literal_column
from shapely.geometry import MultiPoint
from geoalchemy2.shape import from_shape

from skylines.database import db
from skylines.lib import files
from skylines.model import Elevation, IGCFile, Location
from xcsoar import Flight


flightpathfix_fields = ['datetime', 'seconds_of_day',
                        'location', 'gps_altitude', 'pressure_altitude',
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


def run_flight_path(path, max_points=None, qnh=None):
    flight = Flight(path)

    if qnh:
        flight.setQNH(qnh)

    if max_points:
        flight.reduce(threshold=0, max_points=max_points)

    return flight.path()


def flight_path(igc_file, max_points=1000, add_elevation=False, qnh=None):
    if isinstance(igc_file, IGCFile):
        path = files.filename_to_path(igc_file.filename)
    elif isinstance(igc_file, (str, unicode)):
        path = igc_file
    else:
        return None

    output = run_flight_path(path, max_points=max_points, qnh=qnh)

    if add_elevation and len(output):
        output = get_elevation(output)

    return map(lambda line: FlightPathFix(*line), output)


def cumulative_distance(fixes, start_fix, end_fix):
    if start_fix >= end_fix:
        return 0

    distance = 0
    last_location = None

    for fix in fixes[start_fix:end_fix + 1]:
        location = Location(longitude=fix.location['longitude'], latitude=fix.location['latitude'])

        if last_location:
            distance += location.geographic_distance(last_location)

        last_location = location

    return distance


def get_elevation(fixes):
    shortener = int(max(1, len(fixes) / 1000))

    coordinates = [(fix[2]['longitude'], fix[2]['latitude']) for fix in fixes]
    points = MultiPoint(coordinates[::shortener])

    locations = from_shape(points, srid=4326)
    location = locations.ST_DumpPoints()

    cte = db.session.query(location.label('location'),
                           locations.ST_Envelope().label('locations')).cte()

    location_id = literal_column('(location).path[1]')
    elevation = Elevation.rast.ST_Value(cte.c.location.geom)

    # Prepare main query
    q = db.session.query(location_id.label('location_id'), elevation.label('elevation')) \
                  .filter(and_(cte.c.locations.intersects(Elevation.rast),
                               cte.c.location.geom.intersects(Elevation.rast))).all()

    fixes_copy = [list(fix) for fix in fixes]

    # No elevations found at all...
    if not len(q):
        return fixes_copy

    start_idx = 0
    while start_idx < len(q) - 1 and q[start_idx].elevation is None:
        start_idx += 1

    prev = q[start_idx]
    current = None

    for i in xrange(start_idx + 1, len(q)):
        if q[i].elevation is None:
            continue

        current = q[i]

        for j in range((prev.location_id - 1) * shortener, (current.location_id - 1) * shortener):
            elev = prev.elevation + (current.elevation - prev.elevation) / \
                ((current.location_id - prev.location_id) * shortener) * \
                (j - (prev.location_id - 1) * shortener)
            fixes_copy[j][11] = elev

        prev = current

    if len(q) and q[-1].elevation:
        fixes_copy[-1][11] = q[-1].elevation

    return fixes_copy
