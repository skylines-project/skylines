from tempfile import TemporaryFile
from datetime import datetime
from tg import expose, request, redirect, validate, flash
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from tw.forms.fields import SingleSelectField
from tw.forms.validators import FieldStorageUploadConverter
from skylines.controllers.base import BaseController
from skylines.lib import files
from skylines.model import DBSession, User, AircraftModel, Flight
from skylines.lib.md5 import file_md5
from skylines.lib.xcsoar import analyse_flight
from skylines.forms import BootstrapForm, MultiFileField
from zipfile import ZipFile
from skylines.model.igcfile import IGCFile
from skylines.model.notification import create_flight_notifications
from skylines.lib.string import import_ascii


class PilotSelectField(SingleSelectField):
    def update_params(self, d):
        users = DBSession.query(User) \
                .filter(User.club_id == request.identity['user'].club_id) \
                .order_by(User.display_name)
        options = [(None, '[unspecified]')] + \
                  [(user.id, user) for user in users]
        d['options'] = options
        return SingleSelectField.update_params(self, d)


class ModelSelectField(SingleSelectField):
    def update_params(self, d):
        models = DBSession.query(AircraftModel) \
                .order_by(AircraftModel.kind) \
                .order_by(AircraftModel.name) \
                .all()

        gliders = [(model.id, model) for model in models if model.kind == 1]
        motor_gliders = [(model.id, model) for model in models if model.kind == 2]
        hanggliders = [(model.id, model) for model in models if model.kind == 3]
        paragliders = [(model.id, model) for model in models if model.kind == 4]
        ul_gliders = [(model.id, model) for model in models if model.kind == 5]

        options = []

        if len(gliders) > 0: options.append((_('Gliders'), gliders))
        if len(motor_gliders) > 0: options.append((_('Motor Gliders'), motor_gliders))
        if len(hanggliders) > 0: options.append((_('Hanggliders'), hanggliders))
        if len(paragliders) > 0: options.append((_('Paragliders'), paragliders))
        if len(ul_gliders) > 0: options.append((_('UL Gliders'), ul_gliders))

        options.append((_('Other'), [(None, '[unspecified]')]))

        d['options'] = options
        return SingleSelectField.update_params(self, d)

file_field_validator = FieldStorageUploadConverter(
    not_empty=True,
    messages=dict(empty=_("Please add one or more IGC or ZIP files")),
    accept_iterator=True
)

file_field = MultiFileField(
    'file', label_text=l_("IGC or ZIP file(s)"), validator=file_field_validator)

upload_form = BootstrapForm('upload_form', submit_text="Upload", action='do', children=[
    file_field,
    PilotSelectField('pilot', label_text=l_("Pilot"))
])


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
                    form=upload_form,
                    values=dict(pilot=request.identity['user'].id))

    @expose('upload/result.jinja')
    @validate(upload_form, error_handler=index)
    def do(self, file, pilot):
        user = request.identity['user']

        pilot_id = None
        club_id = user.club_id
        if pilot:
            pilot = DBSession.query(User).get(int(pilot))
            if pilot:
                pilot_id = pilot.id
                club_id = pilot.club_id

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

            flights.append((name, flight, None))
            DBSession.add(igc_file)
            DBSession.add(flight)

            create_flight_notifications(flight)

            success = True

        DBSession.flush()

        return dict(flights=flights, success=success,
                    ModelSelectField=ModelSelectField)

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
