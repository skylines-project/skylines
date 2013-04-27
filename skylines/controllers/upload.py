from datetime import datetime
from tempfile import TemporaryFile
from zipfile import ZipFile

from tg import expose, request, redirect, validate, flash
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission

from .base import BaseController
from skylines.forms import upload, aircraft_model
from skylines.lib import files
from skylines.lib.md5 import file_md5
from skylines.lib.string import import_ascii
from skylines.lib.xcsoar import analyse_flight
from skylines.model import DBSession, User, Flight, IGCFile
from skylines.model.notification import create_flight_notifications


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
                yield import_ascii(info.filename), z.open(info.filename, 'r')


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
        return
    elif isinstance(upload, list):
        import logging
        log = logging.getLogger(__name__)
        for x in upload:
            log.info('x=' + repr(x))
            for name, f in IterateUploadFiles(x):
                yield name, f
        return

    for x in IterateFiles(upload.filename, upload.file):
        yield x


class UploadController(BaseController):
    allow_only = has_permission('upload',
                                msg=l_("You have to login to upload flights."))

    @expose('generic/form.jinja')
    def index(self, **kw):
        return dict(active_page='upload', title=_("Upload Flight"),
                    form=upload.form,
                    values=dict(pilot=request.identity['user'].id))

    @expose('upload/result.jinja')
    @validate(upload.form, error_handler=index)
    def do(self, file, pilot):
        user = request.identity['user']

        pilot = pilot and DBSession.query(User).get(int(pilot))
        pilot_id = pilot and pilot.id

        club_id = (pilot and pilot.club_id) or user.club_id

        flights = []
        success = False

        for name, f in IterateUploadFiles(file):
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
            DBSession.add(igc_file)
            DBSession.add(flight)

            create_flight_notifications(flight)

            success = True

        DBSession.flush()

        return dict(flights=flights, success=success,
                    ModelSelectField=aircraft_model.SelectField)

    @expose()
    def update(self, **kw):
        flight_id_list = kw.get('flight_id')
        model_list = kw.get('model')
        registration_list = kw.get('registration')
        competition_id_list = kw.get('competition_id')

        if not isinstance(flight_id_list, list):
            flight_id_list = [flight_id_list]

        if not isinstance(model_list, list):
            model_list = [model_list]

        if not isinstance(registration_list, list):
            registration_list = [registration_list]

        if not isinstance(competition_id_list, list):
            competition_id_list = [competition_id_list]

        if (flight_id_list is None
                or len(flight_id_list) != len(model_list)
                or len(flight_id_list) != len(registration_list)):
            flash(_('Sorry, some error happened when updating your flight(s). Please contact a administrator for help.'), 'warning')
            return redirect('/flights/today')

        for index, id in enumerate(flight_id_list):
            try:
                id = int(id)
            except ValueError:
                continue

            try:
                model_id = int(model_list[index])
            except ValueError:
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

            flight = DBSession.query(Flight).get(id)

            if not flight.is_writable(request.identity):
                continue

            flight.model_id = model_id
            flight.registration = registration
            flight.competition_id = competition_id
            flight.time_modified = datetime.utcnow()

        DBSession.flush()

        flash(_('Your flight(s) have been successfully updated.'))
        return redirect('/flights/today')
