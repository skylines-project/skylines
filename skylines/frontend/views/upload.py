from datetime import datetime
from tempfile import TemporaryFile
from zipfile import ZipFile
from enum import Enum

from flask import Blueprint, render_template, request, flash, redirect, g, current_app, url_for, abort
from flask.ext.babel import _, lazy_gettext as l_
from redis.exceptions import ConnectionError
from werkzeug.exceptions import BadRequest

from skylines.frontend.forms import UploadForm, UploadUpdateForm
from skylines.lib import files
from skylines.lib.decorators import login_required
from skylines.lib.md5 import file_md5
from skylines.lib.xcsoar_ import flight_path, analyse_flight
from skylines.model import db, User, Flight, IGCFile
from skylines.model.event import create_flight_notifications
from skylines.worker import tasks

import xcsoar

upload_blueprint = Blueprint('upload', 'skylines')


class UploadStatus(Enum):
    SUCCESS = 0
    DUPLICATE = 1  # _('Duplicate file')
    MISSING_DATE = 2  # _('Date missing in IGC file')
    PARSER_ERROR = 3  # _('Failed to parse file')
    NO_FLIGHT = 4  # _('No flight found in file')


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


def _get_flight_path(flight):
    fp = flight_path(flight.igc_file, add_elevation=True)

    barogram_h = xcsoar.encode([fix.altitude for fix in fp], method="signed")
    barogram_t = xcsoar.encode([fix.seconds_of_day for fix in fp], method="signed")
    enl = xcsoar.encode([fix.enl if fix.enl is not None else 0 for fix in fp], method="signed")
    elevations_h = xcsoar.encode([fix.elevation if fix.elevation is not None else -1000 for fix in fp], method="signed")

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
            flight_id = request.values.get('{}-sfid'.format(prefix), None, type=int)
            name = request.values.get('{}-name'.format(prefix))

            try:
                status = UploadStatus(request.values.get('{}-status'.format(prefix), type=int))
            except ValueError:
                raise BadRequest('Status unknown')

            flight, trace, form = check_update_form(prefix, flight_id, name, status)

            flights.append((name, flight, status, str(prefix), trace, form))

            if form and form.validate_on_submit():
                _update_flight(flight_id,
                               form.model_id.data,
                               form.registration.data,
                               form.competition_id.data,
                               form.takeoff_time.data,
                               form.scoring_start_time.data,
                               form.scoring_end_time.data,
                               form.landing_time.data)
                flight_id_list.append(flight_id)
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
                flights.append((name, other, UploadStatus.DUPLICATE, str(prefix), None, None))
                continue

        igc_file = IGCFile()
        igc_file.owner = user
        igc_file.filename = filename
        igc_file.md5 = md5
        igc_file.update_igc_headers()

        if igc_file.date_utc is None:
            files.delete_file(filename)
            flights.append((name, None, UploadStatus.MISSING_DATE, str(prefix), None, None))
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

        if not analyse_flight(flight):
            files.delete_file(filename)
            flights.append((name, None, UploadStatus.PARSER_ERROR, str(prefix), None, None))
            continue

        if not flight.takeoff_time or not flight.landing_time:
            files.delete_file(filename)
            flights.append((name, None, UploadStatus.NO_FLIGHT, str(prefix), None, None))
            continue

        if not flight.update_flight_path():
            files.delete_file(filename)
            flights.append((name, None, UploadStatus.NO_FLIGHT, str(prefix), None, None))
            continue

        trace = _get_flight_path(flight)
        flights.append((name, flight, UploadStatus.SUCCESS, str(prefix), trace,
                        UploadUpdateForm(formdata=None, prefix=str(prefix), obj=flight)))

        db.session.add(igc_file)
        db.session.add(flight)

        create_flight_notifications(flight)

        # flush data to make sure we don't get duplicate files from ZIP files
        db.session.flush()

        success = True

    db.session.commit()

    try:
        for flight in flights:
            if flight[2] is UploadStatus.SUCCESS:
                tasks.analyse_flight.delay(flight[1].id)
                tasks.find_meetings.delay(flight[1].id)
    except ConnectionError:
        current_app.logger.info('Cannot connect to Redis server')

    return render_template(
        'upload/result.jinja', num_flights=prefix, flights=flights, success=success)


def check_update_form(prefix, flight_id, name, status):
    if not flight_id:
        return None, None, None

    # Get flight from database and check if it is writable
    flight = Flight.get(flight_id)

    if not flight:
        abort(404)

    if status == UploadStatus.DUPLICATE:
        return flight, None, None

    else:
        if not flight.is_writable(g.current_user):
            abort(403)

        form = UploadUpdateForm(prefix=str(prefix), obj=flight)
        trace = _get_flight_path(flight)

        # Force takeoff_time and landing_time to be within the igc file limits
        if form.takeoff_time.data < trace['igc_start_time']:
            form.takeoff_time.data = trace['igc_start_time']

        if form.landing_time.data > trace['igc_end_time']:
            form.landing_time.data = trace['igc_end_time']

        return flight, trace, form


def _update_flight(flight_id, model_id, registration, competition_id,
                   takeoff_time, scoring_start_time,
                   scoring_end_time, landing_time):
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

    # Set new values
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

    db.session.commit()

    if trigger_analysis:
        analyse_flight(flight)

    return True
