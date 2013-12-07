from datetime import datetime
from tempfile import TemporaryFile
from zipfile import ZipFile

from flask import Blueprint, render_template, request, flash, redirect, g, current_app
from flask.ext.babel import _, lazy_gettext as l_
from redis.exceptions import ConnectionError

from skylines.forms import UploadForm, AircraftModelSelectField
from skylines.lib import files
from skylines.lib.decorators import login_required
from skylines.lib.md5 import file_md5
from skylines.lib.xcsoar_ import analyse_flight
from skylines.model import db, User, Flight, IGCFile
from skylines.model.event import create_flight_notifications
from skylines.worker import tasks

upload_blueprint = Blueprint('upload', 'skylines')


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


@upload_blueprint.route('/', methods=('GET', 'POST'))
@login_required(l_("You have to login to upload flights."))
def index():

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

    for name, f in IterateUploadFiles(form.file.raw_data):
        filename = files.sanitise_filename(name)
        filename = files.add_file(filename, f)

        # check if the file already exists
        with files.open_file(filename) as f:
            md5 = file_md5(f)
            other = Flight.by_md5(md5)
            if other:
                files.delete_file(filename)
                flights.append((name, other, _('Duplicate file')))
                continue

        igc_file = IGCFile()
        igc_file.owner = user
        igc_file.filename = filename
        igc_file.md5 = md5
        igc_file.update_igc_headers()

        if igc_file.date_utc is None:
            files.delete_file(filename)
            flights.append((name, None, _('Date missing in IGC file')))
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
            flights.append((name, None, _('Failed to parse file')))
            continue

        if not flight.takeoff_time or not flight.landing_time:
            files.delete_file(filename)
            flights.append((name, None, _('No flight found in file')))
            continue

        if not flight.update_flight_path():
            files.delete_file(filename)
            flights.append((name, None, _('No flight found in file')))
            continue

        flights.append((name, flight, None))
        db.session.add(igc_file)
        db.session.add(flight)

        create_flight_notifications(flight)

        # flush data to make sure we don't get duplicate files from ZIP files
        db.session.flush()

        success = True

    db.session.commit()

    try:
        for flight in flights:
            if flight[2] is None:
                tasks.analyse_flight.delay(flight[1].id)
    except ConnectionError:
        current_app.logger.info('Cannot connect to Redis server')

    def ModelSelectField(*args, **kwargs):
        return AircraftModelSelectField().bind(None, 'model', *args, **kwargs)()

    return render_template(
        'upload/result.jinja', flights=flights, success=success,
        ModelSelectField=ModelSelectField)


@upload_blueprint.route('/update', methods=['GET', 'POST'])
@login_required(l_("You have to login to upload flights."))
def update():
    flight_id_list = request.values.getlist('flight_id')
    model_list = request.values.getlist('model')
    registration_list = request.values.getlist('registration')
    competition_id_list = request.values.getlist('competition_id')

    if (flight_id_list is None
            or len(flight_id_list) != len(model_list)
            or len(flight_id_list) != len(registration_list)):
        flash(_('Sorry, some error happened when updating your flight(s). Please contact a administrator for help.'), 'warning')
        return redirect('/flights/latest')

    for index, id in enumerate(flight_id_list):
        # Parse flight id

        try:
            id = int(id)
        except ValueError:
            continue

        # Get flight from database and check if it is writable

        flight = Flight.get(id)

        if not flight or not flight.is_writable(g.current_user):
            continue

        # Parse model, registration and competition ID

        try:
            model_id = int(model_list[index])
        except ValueError:
            model_id = None

        if model_id == 0:
            model_id = None

        registration = registration_list[index]
        if registration is not None:
            registration = registration.strip()
            if not 0 < len(registration) < 32:
                registration = None

        competition_id = competition_id_list[index]
        if competition_id is not None:
            competition_id = competition_id.strip()
            if not 0 < len(competition_id) < 5:
                competition_id = None

        # Set new values

        flight.model_id = model_id
        flight.registration = registration
        flight.competition_id = competition_id
        flight.time_modified = datetime.utcnow()

    db.session.commit()

    flash(_('Your flight(s) have been successfully updated.'))
    return redirect('/flights/latest')
