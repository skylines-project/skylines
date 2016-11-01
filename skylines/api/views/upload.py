from datetime import datetime
from tempfile import TemporaryFile
from zipfile import ZipFile
from enum import IntEnum
import hashlib
import os

from collections import namedtuple

from flask import Blueprint, request, current_app, abort, make_response
from redis.exceptions import ConnectionError
from sqlalchemy.sql.expression import func

from skylines.api.json import jsonify
from skylines.api.cache import cache
from skylines.api.oauth import oauth
from skylines.database import db
from skylines.lib import files
from skylines.lib.util import pressure_alt_to_qnh_alt
from skylines.lib.md5 import file_md5
from skylines.lib.sql import query_to_sql
from skylines.lib.xcsoar_ import flight_path, analyse_flight
from skylines.model import User, Flight, IGCFile, Airspace, AircraftModel
from skylines.model.airspace import get_airspace_infringements
from skylines.model.event import create_flight_notifications
from skylines.schemas import fields, AirspaceSchema, AircraftModelSchema, FlightSchema, UserSchema, Schema, ValidationError
from skylines.worker import tasks

from geoalchemy2.shape import from_shape
from sqlalchemy.sql import literal_column
from shapely.geometry import MultiLineString, LineString

try:
    import mapscript
    import pyproj
    mapscript_available = True
except ImportError:
    mapscript_available = False

import xcsoar

upload_blueprint = Blueprint('upload', 'skylines')


class UploadStatus(IntEnum):
    SUCCESS = 0
    DUPLICATE = 1  # _('Duplicate file')
    MISSING_DATE = 2  # _('Date missing in IGC file')
    PARSER_ERROR = 3  # _('Failed to parse file')
    NO_FLIGHT = 4  # _('No flight found in file')
    FLIGHT_IN_FUTURE = 5  # _('Date of flight in future')


class UploadResult(namedtuple('UploadResult', [
        'name', 'flight', 'status', 'prefix', 'trace', 'airspace', 'cache_key'])):

    @classmethod
    def for_duplicate(cls, name, other, prefix):
        return cls(name, other, UploadStatus.DUPLICATE, prefix, None, None, None)

    @classmethod
    def for_missing_date(cls, name, prefix):
        return cls(name, None, UploadStatus.MISSING_DATE, prefix, None, None, None)

    @classmethod
    def for_parser_error(cls, name, prefix):
        return cls(name, None, UploadStatus.PARSER_ERROR, prefix, None, None, None)

    @classmethod
    def for_no_flight(cls, name, prefix):
        return cls(name, None, UploadStatus.NO_FLIGHT, prefix, None, None, None)

    @classmethod
    def for_future_flight(cls, name, prefix):
        return cls(name, None, UploadStatus.FLIGHT_IN_FUTURE, prefix, None, None, None)


class TraceSchema(Schema):
    igc_start_time = fields.DateTime()
    igc_end_time = fields.DateTime()
    barogram_t = fields.String()
    barogram_h = fields.String()
    enl = fields.String()
    elevations_h = fields.String()


class UploadResultSchema(Schema):
    name = fields.String()
    status = fields.Integer()
    flight = fields.Nested(FlightSchema, exclude=('igcFile.owner',))
    trace = fields.Nested(TraceSchema)
    airspaces = fields.Nested(AirspaceSchema, attribute='airspace', many=True)
    cacheKey = fields.String(attribute='cache_key')


def iterate_files(name, f):
    try:
        z = ZipFile(f, 'r')
    except:
        # if f is not a ZipFile

        # reset the pointer to the top of the file
        # (the ZipFile constructor might have moved it!)
        f.seek(0)
        yield name, f
    else:
        # if f is a ZipFile
        for info in z.infolist():
            if info.file_size > 0:
                yield info.filename, z.open(info.filename, 'r')


def iterate_upload_files(upload):
    if isinstance(upload, unicode):
        # the Chromium browser sends an empty string if no file is selected
        if not upload:
            return

        # some Android versions send the IGC file as a string, not as
        # a file
        with TemporaryFile() as f:
            f.write(upload.encode('UTF-8'))
            f.seek(0)
            yield 'direct.igc', f

    elif isinstance(upload, list):
        for x in upload:
            for name, f in iterate_upload_files(x):
                yield name, f

    else:
        for x in iterate_files(upload.filename, upload):
            yield x


def _encode_flight_path(fp, qnh):
    # Reduce to 1000 points maximum with equal spacing
    shortener = int(max(1, len(fp) / 1000))

    barogram_h = xcsoar.encode([pressure_alt_to_qnh_alt(fix.pressure_altitude, qnh) for fix in fp[::shortener]],
                               method="signed")
    barogram_t = xcsoar.encode([fix.seconds_of_day for fix in fp[::shortener]], method="signed")
    enl = xcsoar.encode([fix.enl if fix.enl is not None else 0 for fix in fp[::shortener]], method="signed")
    elevations_h = xcsoar.encode([fix.elevation if fix.elevation is not None else -1000 for fix in fp[::shortener]], method="signed")

    return dict(barogram_h=barogram_h, barogram_t=barogram_t,
                enl=enl, elevations_h=elevations_h,
                igc_start_time=fp[0].datetime, igc_end_time=fp[-1].datetime)


@upload_blueprint.route('/flights/upload', methods=('POST',), strict_slashes=False)
@oauth.required()
def index_post():
    current_user = User.get(request.user_id)

    form = request.form

    if form.get('pilotId') == u'':
        form = form.copy()
        form.pop('pilotId')

    try:
        data = FlightSchema(only=('pilotId', 'pilotName')).load(form).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    pilot_id = data.get('pilot_id')
    pilot = pilot_id and User.get(pilot_id)
    pilot_id = pilot and pilot.id

    club_id = (pilot and pilot.club_id) or current_user.club_id

    results = []

    _files = request.files.getlist('files')

    prefix = 0
    for name, f in iterate_upload_files(_files):
        prefix += 1
        filename = files.sanitise_filename(name)
        filename = files.add_file(filename, f)

        # check if the file already exists
        with files.open_file(filename) as f:
            md5 = file_md5(f)
            other = Flight.by_md5(md5)
            if other:
                files.delete_file(filename)
                results.append(UploadResult.for_duplicate(name, other, str(prefix)))
                continue

        igc_file = IGCFile()
        igc_file.owner = current_user
        igc_file.filename = filename
        igc_file.md5 = md5
        igc_file.update_igc_headers()

        if igc_file.date_utc is None:
            files.delete_file(filename)
            results.append(UploadResult.for_missing_date(name, str(prefix)))
            continue

        flight = Flight()
        flight.pilot_id = pilot_id
        flight.pilot_name = data.get('pilot_name')
        flight.club_id = club_id
        flight.igc_file = igc_file

        flight.model_id = igc_file.guess_model()

        if igc_file.registration:
            flight.registration = igc_file.registration
        else:
            flight.registration = igc_file.guess_registration()

        flight.competition_id = igc_file.competition_id

        fp = flight_path(flight.igc_file, add_elevation=True, max_points=None)

        analyzed = False
        try:
            analyzed = analyse_flight(flight, fp=fp)
        except:
            current_app.logger.exception('analyse_flight() raised an exception')

        if not analyzed:
            files.delete_file(filename)
            results.append(UploadResult.for_parser_error(name, str(prefix)))
            continue

        if not flight.takeoff_time or not flight.landing_time:
            files.delete_file(filename)
            results.append(UploadResult.for_no_flight(name, str(prefix)))
            continue

        if flight.landing_time > datetime.now():
            files.delete_file(filename)
            results.append(UploadResult.for_future_flight(name, str(prefix)))
            continue

        if not flight.update_flight_path():
            files.delete_file(filename)
            results.append(UploadResult.for_no_flight(name, str(prefix)))
            continue

        flight.privacy_level = Flight.PrivacyLevel.PRIVATE

        trace = _encode_flight_path(fp, qnh=flight.qnh)
        infringements = get_airspace_infringements(fp, qnh=flight.qnh)

        db.session.add(igc_file)
        db.session.add(flight)

        # flush data to make sure we don't get duplicate files from ZIP files
        db.session.flush()

        # Store data in cache for image creation
        cache_key = hashlib.sha1(str(flight.id) + '_' + str(current_user.id)).hexdigest()

        cache.set('upload_airspace_infringements_' + cache_key, infringements, timeout=15 * 60)
        cache.set('upload_airspace_flight_path_' + cache_key, fp, timeout=15 * 60)

        airspace = db.session.query(Airspace) \
                             .filter(Airspace.id.in_(infringements.keys())) \
                             .all()

        results.append(UploadResult(name, flight, UploadStatus.SUCCESS, str(prefix), trace, airspace, cache_key))

        create_flight_notifications(flight)

    db.session.commit()

    results = UploadResultSchema().dump(results, many=True).data

    club_members = []
    if current_user.club_id:
        member_schema = UserSchema(only=('id', 'name'))

        club_members = User.query(club_id=current_user.club_id) \
            .order_by(func.lower(User.name)) \
            .filter(User.id != current_user.id)

        club_members = member_schema.dump(club_members.all(), many=True).data

    aircraft_models = AircraftModel.query() \
        .order_by(AircraftModel.kind) \
        .order_by(AircraftModel.name) \
        .all()

    aircraft_models = AircraftModelSchema().dump(aircraft_models, many=True).data

    return jsonify(results=results, club_members=club_members, aircraft_models=aircraft_models)


@upload_blueprint.route('/flights/upload/verify', methods=('POST',))
@oauth.required()
def verify():
    current_user = User.get(request.user_id)

    json = request.get_json()
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = FlightSchema(partial=True).load(json, many=True).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    ids = [it.get('id') for it in data]
    if not all(ids):
        return jsonify(error='id-missing'), 422

    user_ids = [it['pilot_id'] for it in data if 'pilot_id' in it]
    user_ids.extend([it['co_pilot_id'] for it in data if 'co_pilot_id' in it])

    model_ids = [it['model_id'] for it in data if 'model_id' in it]

    flights = {flight.id: flight for flight in Flight.query().filter(Flight.id.in_(ids)).all()}
    users = {user.id: user for user in User.query().filter(User.id.in_(user_ids)).all()}
    models = {model.id: model for model in AircraftModel.query().filter(AircraftModel.id.in_(model_ids)).all()}

    for d in data:
        flight = flights.get(d.pop('id'))
        if not flight or not flight.is_writable(current_user):
            return jsonify(error='unknown-flight'), 422

        if 'pilot_id' in d and d['pilot_id'] is not None and d['pilot_id'] not in users:
            return jsonify(error='unknown-pilot'), 422

        if 'co_pilot_id' in d and d['co_pilot_id'] is not None and d['co_pilot_id'] not in users:
            return jsonify(error='unknown-copilot'), 422

        if 'model_id' in d and d['model_id'] is not None and d['model_id'] not in models:
            return jsonify(error='unknown-aircraft-model'), 422

        for key in ('takeoff_time', 'scoring_start_time', 'scoring_end_time', 'landing_time'):
            if key in d:
                d[key] = d[key].replace(tzinfo=None)

        old_pilot = flight.pilot_id

        for key, value in d.iteritems():
            setattr(flight, key, value)

        if not (flight.takeoff_time <= flight.scoring_start_time <= flight.scoring_end_time <= flight.landing_time):
            return jsonify(error='invalid-times'), 422

        if flight.pilot_id != old_pilot and flight.pilot_id:
            flight.club_id = users[flight.pilot_id].club_id

        flight.privacy_level = Flight.PrivacyLevel.PUBLIC
        flight.time_modified = datetime.utcnow()

    db.session.commit()

    for flight_id in flights.iterkeys():
        try:
            tasks.analyse_flight.delay(flight_id)
            tasks.find_meetings.delay(flight_id)
        except ConnectionError:
            current_app.logger.info('Cannot connect to Redis server')

    return jsonify()


@upload_blueprint.route('/flights/upload/airspace/<string:cache_key>/<int:airspace_id>.png')
def airspace_image(cache_key, airspace_id):
    if not mapscript_available:
        abort(404)

    # get information from cache...
    infringements = cache.get('upload_airspace_infringements_' + cache_key)
    flight_path = cache.get('upload_airspace_flight_path_' + cache_key)

    # abort if invalid cache key
    if not infringements \
       or not flight_path:
        abort(404)

    # Convert the coordinate into a list of tuples
    coordinates = [(c.location['longitude'], c.location['latitude']) for c in flight_path]
    # Create a shapely LineString object from the coordinates
    linestring = LineString(coordinates)
    # Save the new path as WKB
    locations = from_shape(linestring, srid=4326)

    highlight_locations = []
    extent_epsg4326 = [180, 85.05112878, -180, -85.05112878]

    for period in infringements[airspace_id]:
        # Convert the coordinate into a list of tuples
        coordinates = [(c['location']['longitude'], c['location']['latitude']) for c in period]

        # Create a shapely LineString object from the coordinates
        if len(coordinates) == 1:
            # a LineString must contain at least two points...
            linestring = LineString([coordinates[0], coordinates[0]])
        else:
            linestring = LineString(coordinates)

        highlight_locations.append(linestring)

        # gather extent
        (minx, miny, maxx, maxy) = linestring.bounds

        extent_epsg4326[0] = min(extent_epsg4326[0], minx)
        extent_epsg4326[1] = min(extent_epsg4326[1], miny)
        extent_epsg4326[2] = max(extent_epsg4326[2], maxx)
        extent_epsg4326[3] = max(extent_epsg4326[3], maxy)

    # Save the new path as WKB
    highlight_multilinestring = from_shape(MultiLineString(highlight_locations), srid=4326)

    # increase extent by factor 1.05
    width = abs(extent_epsg4326[0] - extent_epsg4326[2])
    height = abs(extent_epsg4326[1] - extent_epsg4326[3])

    center_x = (extent_epsg4326[0] + extent_epsg4326[2]) / 2
    center_y = (extent_epsg4326[1] + extent_epsg4326[3]) / 2

    extent_epsg4326[0] = center_x - width / 2 * 1.05
    extent_epsg4326[1] = center_y - height / 2 * 1.05
    extent_epsg4326[2] = center_x + width / 2 * 1.05
    extent_epsg4326[3] = center_y + height / 2 * 1.05

    # minimum extent should be 0.3 deg
    width = abs(extent_epsg4326[0] - extent_epsg4326[2])
    height = abs(extent_epsg4326[1] - extent_epsg4326[3])

    if width < 0.3:
        extent_epsg4326[0] = center_x - 0.15
        extent_epsg4326[2] = center_x + 0.15

    if height < 0.3:
        extent_epsg4326[1] = center_y - 0.15
        extent_epsg4326[3] = center_y + 0.15

    # convert extent from EPSG4326 to EPSG3857
    epsg4326 = pyproj.Proj(init='epsg:4326')
    epsg3857 = pyproj.Proj(init='epsg:3857')

    x1, y1 = pyproj.transform(epsg4326, epsg3857, extent_epsg4326[0], extent_epsg4326[1])
    x2, y2 = pyproj.transform(epsg4326, epsg3857, extent_epsg4326[2], extent_epsg4326[3])

    extent_epsg3857 = [x1, y1, x2, y2]

    # load basemap and set size + extent
    basemap_path = os.path.join(current_app.config.get('SKYLINES_MAPSERVER_PATH'), 'basemap.map')
    map_object = mapscript.mapObj(basemap_path)
    map_object.setSize(400, 400)
    map_object.setExtent(extent_epsg3857[0], extent_epsg3857[1], extent_epsg3857[2], extent_epsg3857[3])

    # enable airspace and airports layers
    num_layers = map_object.numlayers
    for i in range(num_layers):
        layer = map_object.getLayer(i)

        if layer.group == 'Airports':
            layer.status = mapscript.MS_ON

        if layer.group == 'Airspace':
            layer.status = mapscript.MS_ON

    # get flights layer
    flights_layer = map_object.getLayerByName('Flights')
    highlight_layer = map_object.getLayerByName('Flights_Highlight')

    # set sql query for blue flight
    one = literal_column('1 as flight_id')
    flight_query = db.session.query(locations.label('flight_geometry'), one)

    flights_layer.data = 'flight_geometry FROM (' + query_to_sql(flight_query) + ')' + \
                         ' AS foo USING UNIQUE flight_id USING SRID=4326'

    # set sql query for highlighted linestrings
    highlighted_query = db.session.query(highlight_multilinestring.label('flight_geometry'), one)

    highlight_layer.data = 'flight_geometry FROM (' + query_to_sql(highlighted_query) + ')' + \
                           ' AS foo USING UNIQUE flight_id USING SRID=4326'

    highlight_layer.status = mapscript.MS_ON

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
