from tg import expose, request, redirect, flash
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from tw.forms import TableForm
from tw.forms.fields import FileField, SingleSelectField
from skylines.lib.base import BaseController
from skylines import files
from skylines.model import DBSession, User, Flight
from skylines.lib.analysis import analyse_flight

class PilotSelectField(SingleSelectField):
    def update_params(self, d):
        users = DBSession.query(User).filter(User.club_id == request.identity['user'].club_id)
        options = [(None, '[unspecified]')] + \
                  [(user.user_id, user) for user in users]
        d['options'] = options
        return SingleSelectField.update_params(self, d)

upload_form = TableForm('upload_form', submit_text="Upload", action='do', children=[
    FileField('file', label_text="IGC or ZIP file"),
    PilotSelectField('pilot', label_text="Pilot"),
])

def IterateFiles(name, f):
    from zipfile import ZipFile
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

class UploadController(BaseController):
    allow_only = has_permission('upload',
                                msg=l_("You don't have permission to upload flights."))

    @expose('skylines.templates.upload.index')
    def index(self):
        return dict(page='upload', form=upload_form)

    @expose('skylines.templates.upload.result')
    def do(self, file, pilot):
        user = request.identity['user']

        flights = []

        for name, f in IterateFiles(file.filename, file.file):
            filename = files.sanitise_filename(name)
            filename = files.add_file(filename, f)

            flight = Flight()
            flight.owner = user
            flight.filename = filename
            flight.club_id = user.club_id
            flight.pilot_id = pilot

            if not analyse_flight(flight):
                files.delete_file(filename)
                flights.append((name, None, _('Failed to parse file')))
                continue

            other = flight.by_md5(flight.md5)
            if other:
                files.delete_file(filename)
                flights.append((name, other, _('Duplicate file')))
                continue

            flights.append((name, flight, None))
            DBSession.add(flight)

        DBSession.flush()

        return dict(page='upload', flights=flights)

    @expose('skylines.templates.upload.result')
    def test(self):
        return dict(page='upload', flights=[('foo.igc', None, None),('bar.igc', None, 'Error!')])
