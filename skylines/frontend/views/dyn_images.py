from flask import Blueprint, make_response, abort, request, g, redirect, current_app

from datetime import datetime
import pyproj
import re
import math
import os
from sqlalchemy import func
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.orm.util import aliased

try:
    import mapscript
    mapscript_available = True
except ImportError:
    mapscript_available = False

from skylines.model import db, Flight, User, Club, Airport, Boundaries
from skylines.lib.dbutil import get_requested_record
from skylines.lib.geo import zoom_bounding_box

dyn_images_blueprint = Blueprint('dyn_images', 'skylines')


@dyn_images_blueprint.route('/overview/<string:type>/<string:country_code>/<value>/map.png')
@dyn_images_blueprint.route('/overview/<string:type>/<string:country_code>/map.png')
def overview(type, country_code, value=None):
    if type == 'all' or type == None:
        extent = _guess_extent(country_code)
        f = None

    elif type == 'date':
        try:
            if isinstance(value, (str, unicode)):
                date = datetime.strptime(value, "%Y-%m-%d")

            elif isinstance(value, datetime):
                date = value.date()

            else:
                abort(404)
        except:
            abort(404)

        extent = _guess_extent(country_code)
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

    pilot_alias = aliased(User, name='pilot')

    q = db.session.query(Flight,
                         Flight.locations.label('flight_geometry'),
                         Flight.id.label('flight_id')) \
        .join(Flight.igc_file) \
        .options(contains_eager(Flight.igc_file)) \
        .outerjoin(pilot_alias, Flight.pilot) \
        .options(contains_eager(Flight.pilot, alias=pilot_alias)) \
        .options(joinedload(Flight.co_pilot)) \
        .outerjoin(Flight.club) \
        .options(contains_eager(Flight.club)) \
        .outerjoin(Flight.takeoff_airport) \
        .options(contains_eager(Flight.takeoff_airport)) \
        .filter(Flight.is_listable(g.current_user))

    if f is not None:
        q = q.filter(f)

    modified = q.order_by(Flight.time_modified.desc()).first()

    if modified:
        last_modified = modified.Flight.time_modified
    else:
        last_modified = None

    cache_key = 'overview_image_' + type + \
                '_' + country_code + \
                '_' + str(value) + \
                '_' + str(last_modified)

    overview_image = current_app.cache.get(cache_key)

    if not overview_image:
        overview_image = _create_overview(query=q, extent=extent)
        current_app.cache.set(cache_key, overview_image, timeout=3600 * 24)

    return overview_image


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


def _guess_extent(country_code):
    # maximum and default extent of epsg3857
    extent = [-180, -85.05112878, 180, 85.05112878]

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
    if not mapscript_available:
        return redirect('/images/no_mapscript_available.png')

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

        extent_epsg4326 = zoom_bounding_box(extent_epsg4326, 1.05)

    # limit extent to EPSG3857 maximum extent
    if abs(extent_epsg4326[0]) > 180:
        extent_epsg4326[0] = math.copysign(180, extent_epsg4326[0])

    if abs(extent_epsg4326[1]) > 85.05112878:
        extent_epsg4326[1] = math.copysign(85.05112878, extent_epsg4326[1])

    if abs(extent_epsg4326[2]) > 180:
        extent_epsg4326[2] = math.copysign(180, extent_epsg4326[2])

    if abs(extent_epsg4326[3]) > 85.05112878:
        extent_epsg4326[3] = math.copysign(85.05112878, extent_epsg4326[3])

    # convert extent from EPSG4326 to EPSG3857
    epsg4326 = pyproj.Proj(init='epsg:4326')
    epsg3857 = pyproj.Proj(init='epsg:3857')

    x1, y1 = pyproj.transform(epsg4326, epsg3857, extent_epsg4326[0], extent_epsg4326[1])
    x2, y2 = pyproj.transform(epsg4326, epsg3857, extent_epsg4326[2], extent_epsg4326[3])

    extent_epsg3857 = [x1, y1, x2, y2]

    # load basemap and set size + extent
    map_object = mapscript.mapObj(
        os.path.join(current_app.config.get('SKYLINES_MAPSERVER_BASEDIR', 'mapserver'),
                     'flight_overview.map'))

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
