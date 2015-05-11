from datetime import datetime
from tempfile import TemporaryFile
from zipfile import ZipFile
from enum import Enum
import hashlib
import os

from flask import Blueprint, render_template, request, flash, redirect, g, current_app, url_for, abort, make_response
from flask.ext.babel import _, lazy_gettext as l_
from redis.exceptions import ConnectionError
from werkzeug.exceptions import BadRequest

from skylines.database import db
from skylines.frontend.forms import UploadForm, UploadUpdateForm
from skylines.lib import files
from skylines.lib.util import pressure_alt_to_qnh_alt
from skylines.lib.decorators import login_required
from skylines.lib.md5 import file_md5
from skylines.lib.sql import query_to_sql
from skylines.lib.xcsoar_ import flight_path, analyse_flight
from skylines.model import User, Flight, IGCFile, Airspace
from skylines.model.airspace import get_airspace_infringements
from skylines.model.event import create_flight_notifications
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


class UploadStatus(Enum):
    SUCCESS = 0
    DUPLICATE = 1  # _('Duplicate file')
    MISSING_DATE = 2  # _('Date missing in IGC file')
    PARSER_ERROR = 3  # _('Failed to parse file')
    NO_FLIGHT = 4  # _('No flight found in file')
    FLIGHT_IN_FUTURE = 5  # _('Date of flight in future')


def IterateFiles(name, f):
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


def IterateUploadFiles(upload):
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
            for name, f in IterateUploadFiles(x):
                yield name, f

    else:
        for x in IterateFiles(upload.filename, upload):
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


@upload_blueprint.route('/', methods=('GET', 'POST'))
@login_required(l_("You have to login to upload flights."))
def index():
    if request.values.get('stage', type=int) == 1:
        # Parse update form
        num_flights = request.values.get('num_flights', 0, type=int)

        flights = []
        flight_id_list = []
        form_error = False

        for prefix in range(1, num_flights + 1):
            name = request.values.get('{}-name'.format(prefix))

            try:
                status = UploadStatus(request.values.get('{}-status'.format(prefix), type=int))
            except ValueError:
                raise BadRequest('Status unknown')

            flight, fp, form = check_update_form(prefix, status)

            if fp:
                trace = _encode_flight_path(fp, flight.qnh)
                infringements = get_airspace_infringements(fp, qnh=flight.qnh)
            else:
                trace = None
                infringements = {}

            cache_key = None

            if form and not infringements:
                # remove airspace field from form if no airspace infringements found
                del form.airspace_usage

            elif form and infringements:
                # if airspace infringements found create cache_key from flight id and user id
                cache_key = hashlib.sha1(str(flight.id) + '_' + str(g.current_user.id)).hexdigest()

            airspace = db.session.query(Airspace) \
                                 .filter(Airspace.id.in_(infringements.keys())) \
                                 .all()

            flights.append((name, flight, status, str(prefix), trace, airspace, cache_key, form))

            if form and form.validate_on_submit():
                _update_flight(flight.id,
                               fp,
                               form.model_id.data,
                               form.registration.data,
                               form.competition_id.data,
                               form.takeoff_time.data,
                               form.scoring_start_time.data,
                               form.scoring_end_time.data,
                               form.landing_time.data,
                               form.pilot_id.data, form.pilot_name.data,
                               form.co_pilot_id.data, form.co_pilot_name.data)
                flight_id_list.append(flight.id)
            elif form:
                form_error = True

        if form_error:
            return render_template(
                'upload/result.jinja', num_flights=num_flights, flights=flights, success=True)
        elif flight_id_list:
            flash(_('Your flight(s) have been successfully published.'))
            return redirect(url_for('flights.list', ids=','.join(str(x) for x in flight_id_list)))
        else:
            return redirect(url_for('flights.today'))

    else:
        # Create/parse file selection form
        form = UploadForm(pilot=g.current_user.id)

        if form.validate_on_submit():
            return index_post(form)

        return render_template('upload/form.jinja', form=form)


def index_post(form):
    user = g.current_user

    pilot_id = form.pilot.data if form.pilot.data != 0 else None
    pilot = pilot_id and User.get(int(pilot_id))
    pilot_id = pilot and pilot.id

    club_id = (pilot and pilot.club_id) or user.club_id

    flights = []
    success = False

    prefix = 0
    for name, f in IterateUploadFiles(form.file.raw_data):
        prefix += 1
        filename = files.sanitise_filename(name)
        filename = files.add_file(filename, f)

        # check if the file already exists
        with files.open_file(filename) as f:
            md5 = file_md5(f)
            other = Flight.by_md5(md5)
            if other:
                files.delete_file(filename)
                flights.append((name, other, UploadStatus.DUPLICATE, str(prefix), None, None, None, None))
                continue

        igc_file = IGCFile()
        igc_file.owner = user
        igc_file.filename = filename
        igc_file.md5 = md5
        igc_file.update_igc_headers()

        if igc_file.date_utc is None:
            files.delete_file(filename)
            flights.append((name, None, UploadStatus.MISSING_DATE, str(prefix), None, None, None, None))
            continue

        flight = Flight()
        flight.pilot_id = pilot_id
        flight.pilot_name = form.pilot_name.data if form.pilot_name.data else None
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
            analyse_flight(flight, fp=fp)
            analyzed = True
        except:
            current_app.logger.exception('analyse_flight() raised an exception')

        if not analyzed:
            files.delete_file(filename)
            flights.append((name, None, UploadStatus.PARSER_ERROR, str(prefix), None, None, None, None))
            continue

        if not flight.takeoff_time or not flight.landing_time:
            files.delete_file(filename)
            flights.append((name, None, UploadStatus.NO_FLIGHT, str(prefix), None, None, None, None))
            continue

        if flight.landing_time > datetime.now():
            files.delete_file(filename)
            flights.append((name, None, UploadStatus.FLIGHT_IN_FUTURE, str(prefix), None, None, None, None))
            continue

        if not flight.update_flight_path():
            files.delete_file(filename)
            flights.append((name, None, UploadStatus.NO_FLIGHT, str(prefix), None, None, None, None))
            continue

        flight.privacy_level = Flight.PrivacyLevel.PRIVATE

        trace = _encode_flight_path(fp, qnh=flight.qnh)
        infringements = get_airspace_infringements(fp, qnh=flight.qnh)

        db.session.add(igc_file)
        db.session.add(flight)

        # flush data to make sure we don't get duplicate files from ZIP files
        db.session.flush()

        # Store data in cache for image creation
        cache_key = hashlib.sha1(str(flight.id) + '_' + str(user.id)).hexdigest()

        current_app.cache.set('upload_airspace_infringements_' + cache_key, infringements, timeout=15 * 60)
        current_app.cache.set('upload_airspace_flight_path_' + cache_key, fp, timeout=15 * 60)

        airspace = db.session.query(Airspace) \
                             .filter(Airspace.id.in_(infringements.keys())) \
                             .all()

        # create form after flushing the session, otherwise we wouldn't have a flight.id
        form = UploadUpdateForm(formdata=None, prefix=str(prefix), obj=flight)
        # remove airspace field from form if no airspace infringements found
        if not infringements:
            del form.airspace_usage

        # replace None in form.pilot_id and form.co_pilot_id with 0
        if not form.pilot_id.data: form.pilot_id.data = 0
        if not form.co_pilot_id.data: form.co_pilot_id.data = 0

        form.pilot_id.validate(form)

        flights.append((name, flight, UploadStatus.SUCCESS, str(prefix), trace,
                        airspace, cache_key, form))

        create_flight_notifications(flight)

        success = True

    db.session.commit()

    if success:
        flash(_('Please click "Publish Flight(s)" at the bottom to confirm our automatic analysis.'))

    return render_template(
        'upload/result.jinja', num_flights=prefix, flights=flights, success=success)


def check_update_form(prefix, status):
    form = UploadUpdateForm(prefix=str(prefix))

    if not form.id or not form.id.data:
        return None, None, None

    flight_id = form.id.data

    # Get flight from database and check if it is writable
    flight = Flight.get(flight_id)

    if not flight:
        abort(404)

    if status == UploadStatus.DUPLICATE:
        return flight, None, None

    else:
        if not flight.is_writable(g.current_user):
            abort(403)

        fp = flight_path(flight.igc_file, add_elevation=True, max_points=None)

        form.populate_obj(flight)

        # replace None in form.pilot_id and form.co_pilot_id with 0
        if not form.pilot_id.data: form.pilot_id.data = 0
        if not form.co_pilot_id.data: form.co_pilot_id.data = 0

        # Force takeoff_time and landing_time to be within the igc file limits
        if form.takeoff_time.data < fp[0].datetime:
            form.takeoff_time.data = fp[0].datetime

        if form.landing_time.data > fp[-1].datetime:
            form.landing_time.data = fp[-1].datetime

        return flight, fp, form


def _update_flight(flight_id, fp, model_id, registration, competition_id,
                   takeoff_time, scoring_start_time,
                   scoring_end_time, landing_time,
                   pilot_id, pilot_name,
                   co_pilot_id, co_pilot_name):
    # Get flight from database and check if it is writable
    flight = Flight.get(flight_id)

    if not flight or not flight.is_writable(g.current_user):
        return False

    # Parse model, registration and competition ID
    if model_id == 0:
        model_id = None

    if registration is not None:
        registration = registration.strip()
        if not 0 < len(registration) <= 32:
            registration = None

    if competition_id is not None:
        competition_id = competition_id.strip()
        if not 0 < len(competition_id) <= 5:
            competition_id = None

    if pilot_id == 0:
        pilot_id = None

    # Set new values
    if flight.pilot_id != pilot_id:
        flight.pilot_id = pilot_id

        # update club if pilot changed
        if pilot_id:
            flight.club_id = User.get(pilot_id).club_id

    flight.pilot_name = pilot_name if pilot_name else None

    flight.co_pilot_id = co_pilot_id if co_pilot_id != 0 else None
    flight.co_pilot_name = co_pilot_name if co_pilot_name else None

    flight.model_id = model_id
    flight.registration = registration
    flight.competition_id = competition_id
    flight.time_modified = datetime.utcnow()

    # Update times only if they are reasonable and have been changed...
    trigger_analysis = False

    if takeoff_time and scoring_start_time and scoring_end_time and landing_time \
       and takeoff_time <= scoring_start_time <= scoring_end_time <= landing_time \
       and (flight.takeoff_time != takeoff_time
            or flight.scoring_start_time != scoring_start_time
            or flight.scoring_end_time != scoring_end_time
            or flight.landing_time != landing_time):

        flight.takeoff_time = takeoff_time
        flight.scoring_start_time = scoring_start_time
        flight.scoring_end_time = scoring_end_time
        flight.landing_time = landing_time

        trigger_analysis = True

    flight.privacy_level = Flight.PrivacyLevel.PUBLIC

    db.session.commit()

    if trigger_analysis:
        analyse_flight(flight, fp=fp)

    try:
        tasks.analyse_flight.delay(flight.id)
        tasks.find_meetings.delay(flight.id)
    except ConnectionError:
        current_app.logger.info('Cannot connect to Redis server')

    return True


@upload_blueprint.route('/airspace/<string:cache_key>/<int:as_id>.png')
def airspace_image(cache_key, as_id):
    if not mapscript_available:
        abort(404)

    # get information from cache...
    infringements = current_app.cache.get('upload_airspace_infringements_' + cache_key)
    flight_path = current_app.cache.get('upload_airspace_flight_path_' + cache_key)

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

    for period in infringements[as_id]:
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
