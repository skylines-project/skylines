from flask import Blueprint, make_response, abort, request, g, current_app

from datetime import datetime
import mapscript
import pyproj
import re
from sqlalchemy import func
from sqlalchemy.sql.expression import or_

from skylines.model import db, Flight, User, Club, Airport, Boundaries
from skylines.lib.dbutil import get_requested_record
from skylines.lib.geo import zoom_bounding_box

dyn_images_blueprint = Blueprint('dyn_images', 'skylines')


@dyn_images_blueprint.route('/overview/<string:type>/<value>/map.png')
def overview(type=None, value=None):
    if type == 'all' or type == None:
        extent = _guess_extent()
        f = None

    elif type == 'date':
        try:
            if isinstance(value, (str, unicode)):
                date = datetime.strptime(value, "%Y-%m-%d")

            if isinstance(value, datetime):
                date = value.date()

        except:
            abort(404)

        extent = _guess_extent()
        f = Flight.date_local == date

    elif type == 'pilot':
        try:
            pilot = get_requested_record(User, int(value))
        except:
            abort(404)

        extent = None
        f = or_(Flight.pilot == pilot,
                Flight.co_pilot == pilot)

    elif type == 'club':
        try:
            club = get_requested_record(Club, int(value))
        except:
            abort(404)

        extent = None
        f = Flight.club == club

    elif type == 'airport':
        try:
            airport = get_requested_record(Airport, int(value))
        except:
            abort(404)

        extent = None
        f = Flight.takeoff_airport == airport

    elif type == 'pinned':
        # Check if we have cookies
        if request.cookies is None:
            abort(404)

        # Check for the 'pinnedFlights' cookie
        ids = request.cookies.get('SkyLines_pinnedFlights', None)
        if not ids:
            abort(404)

        try:
            # Split the string into integer IDs (%2C = comma)
            ids = [int(id) for id in ids.split('%2C')]
        except ValueError:
            abort(404)

        extent = None
        f = Flight.id.in_(ids)

    q = db.session.query(Flight.locations.label('flight_geometry'),
                         Flight.locations.label('flight_id')) \
        .filter(Flight.is_listable(g.current_user))

    if f is not None:
        q = q.filter(f)

    return _create_overview(query=q, extent=extent)


def _query_to_sql(query):
    '''
    Convert a sqlalchemy query to raw SQL.
    https://stackoverflow.com/questions/4617291/how-do-i-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression
    '''

    from psycopg2.extensions import adapt as sqlescape

    statement = query.statement.compile(dialect=query.session.bind.dialect)
    dialect = query.session.bind.dialect

    enc = dialect.encoding
    params = {}

    for k, v in statement.params.iteritems():
        if isinstance(v, unicode):
            v = v.encode(enc)
        params[k] = sqlescape(v)

    return (statement.string.encode(enc) % params).decode(enc)


def _guess_extent():
    import GeoIP

    # maximum and default extent of epsg3857
    extent = [-180, -85.05112878, 180, 85.05112878]

    geoip = GeoIP.open(current_app.config.get('GEOIP_DATABASE'), GeoIP.GEOIP_STANDARD)
    country_code = geoip.country_code_by_addr(request.remote_addr)

    if not country_code:
        return extent

    extent_q = db.session.query(func.ST_Extent(Boundaries.geometry).label('extent')) \
        .filter(func.lower(Boundaries.iso_a2) == func.lower(country_code))

    if extent_q.scalar():
        m = re.match("BOX\(([-+]?[0-9]*\.?[0-9]+) ([-+]?[0-9]*\.?[0-9]+)," +
                     "([-+]?[0-9]*\.?[0-9]+) ([-+]?[0-9]*\.?[0-9]+)\)", extent_q.scalar())
        if m:
            extent[0] = float(m.group(1))
            extent[1] = float(m.group(2))
            extent[2] = float(m.group(3))
            extent[3] = float(m.group(4))

    return zoom_bounding_box(extent, 1.2)


def _create_overview(query, extent):
    if extent:
        extent_epsg4326 = extent
    else:
        # maximum and default extent of epsg3857
        extent_epsg4326 = [-180, -85.05112878, 180, 85.05112878]

        extent_q = db.session.query(func.ST_Extent(query.subquery().c.flight_geometry)
                                        .label('extent'))

        m = re.match("BOX\(([-+]?[0-9]*\.?[0-9]+) ([-+]?[0-9]*\.?[0-9]+)," +
                     "([-+]?[0-9]*\.?[0-9]+) ([-+]?[0-9]*\.?[0-9]+)\)", extent_q.scalar())
        if m:
            extent_epsg4326[0] = float(m.group(1))
            extent_epsg4326[1] = float(m.group(2))
            extent_epsg4326[2] = float(m.group(3))
            extent_epsg4326[3] = float(m.group(4))

    # convert extent from EPSG4326 to EPSG3857
    epsg4326 = pyproj.Proj(init='epsg:4326')
    epsg3857 = pyproj.Proj(init='epsg:3857')

    x1, y1 = pyproj.transform(epsg4326, epsg3857, extent_epsg4326[0], extent_epsg4326[1])
    x2, y2 = pyproj.transform(epsg4326, epsg3857, extent_epsg4326[2], extent_epsg4326[3])

    extent_epsg3857 = [x1, y1, x2, y2]

    # load basemap and set size + extent
    map_object = mapscript.mapObj('mapserver/flight_overview.map')
    map_object.setSize(400, 500)
    map_object.setExtent(extent_epsg3857[0], extent_epsg3857[1], extent_epsg3857[2], extent_epsg3857[3])

    # enable airspace and airports layers
    num_layers = map_object.numlayers
    for i in range(num_layers):
        layer = map_object.getLayer(i)

        if layer.group == 'Airports':
            layer.status = mapscript.MS_ON

    # get flights layer
    flights_layer = map_object.getLayerByName('Flights')

    # set sql query
    flights_layer.data = 'flight_geometry FROM (' + _query_to_sql(query) + ')' + \
                         ' AS foo USING UNIQUE flight_id USING SRID=4326'

    # get osm layer and set WMS url
    osm_layer = map_object.getLayerByName('OSM')
    osm_layer.connection = current_app.config.get('SKYLINES_MAP_TILE_URL') + \
        '/service?'

    # draw map
    map_image = map_object.draw()

    # get image
    mapscript.msIO_installStdoutToBuffer()
    map_image.write()
    content = mapscript.msIO_getStdoutBufferBytes()

    # return to client
    resp = make_response(content)
    resp.headers['Content-type'] = map_image.format.mimetype
    return resp
