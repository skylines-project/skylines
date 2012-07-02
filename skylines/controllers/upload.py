from tempfile import TemporaryFile
from tg import expose, request, redirect, flash, validate
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from tw.forms.fields import TextField, SingleSelectField
from tw.forms.validators import FieldStorageUploadConverter
from skylines.lib.base import BaseController
from skylines import files
from skylines.model import DBSession, User, Model, Flight
from skylines.lib.md5 import file_md5
from skylines.lib.igc import read_igc_header
from skylines.lib.analysis import analyse_flight
from skylines.form import BootstrapForm, MultiFileField
from zipfile import ZipFile
from skylines.model.igcfile import IGCFile

class PilotSelectField(SingleSelectField):
    def update_params(self, d):
        users = DBSession.query(User) \
                .filter(User.club_id == request.identity['user'].club_id) \
                .order_by(User.display_name)
        options = [(None, '[unspecified]')] + \
                  [(user.user_id, user) for user in users]
        d['options'] = options
        return SingleSelectField.update_params(self, d)

class ModelSelectField(SingleSelectField):
    def update_params(self, d):
        models = DBSession.query(Model) \
                .order_by(Model.name)
        options = [(None, '[unspecified]')] + \
                  [(model.id, model) for model in models]
        d['options'] = options
        return SingleSelectField.update_params(self, d)

upload_form = BootstrapForm('upload_form', submit_text="Upload", action='do', children=[
    MultiFileField('file', label_text="IGC or ZIP file",
        validator=FieldStorageUploadConverter(not_empty=True, messages=dict(empty=_("Please add a IGC or ZIP file"))) ),
    PilotSelectField('pilot', label_text="Pilot"),
    ModelSelectField('model', label_text="Aircraft model"),
    TextField('registration', label_text="Aircraft registration"),
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
        return
    elif isinstance(upload, list):
        import logging
        log = logging.getLogger(__name__)
        for x in upload:
            log.info('x='+repr(x))
            for name, f in IterateUploadFiles(x):
                yield name, f
        return

    for x in IterateFiles(upload.filename, upload.file):
        yield x

class UploadController(BaseController):
    allow_only = has_permission('upload',
                                msg=l_("You have to login to upload flights."))

    @expose('skylines.templates.generic.form')
    def index(self, **kw):
        return dict(page='upload', title=_("Upload Flight"),
                    form=upload_form,
                    values=dict(pilot=request.identity['user'].user_id))

    @expose('skylines.templates.upload.result')
    @validate(upload_form, error_handler=index)
    def do(self, file, pilot, model, registration):
        user = request.identity['user']

        pilot_id = None
        club_id = user.club_id
        if pilot:
            pilot = DBSession.query(User).get(int(pilot))
            if pilot:
                pilot_id = pilot.user_id
                club_id = pilot.club_id

        model_id = None
        if model:
            model = DBSession.query(Model).get(int(model))
            if model:
                model_id = model.id

        if registration is not None:
            registration = registration.strip()
            if len(registration) == 0:
                registration = None

        flights = []

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
            read_igc_header(igc_file)

            flight = Flight()
            flight.pilot_id = pilot_id
            flight.club_id = club_id
            flight.model_id = model_id
            flight.registration = registration
            flight.igc_file = igc_file

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

        DBSession.flush()

        return dict(page='upload', flights=flights)
