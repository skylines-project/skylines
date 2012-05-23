from tg import expose, request, redirect, flash
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from skylines.lib.base import BaseController
from skylines import files
from skylines.model import DBSession, Flight
from skylines.lib.analysis import analyse_flight

def IterateFiles(name, f):
    from zipfile import ZipFile
    try:
        z = ZipFile(f, 'r')
    except:
        f.seek(0)
        yield name, f
    else:
        for info in z.infolist():
            if info.file_size > 0:
                yield info.filename, z.open(info.filename, 'r')

class UploadController(BaseController):
    allow_only = has_permission('upload',
                                msg=l_("You don't have permission to upload flights."))

    @expose('skylines.templates.upload.index')
    def index(self):
        return dict(page = 'upload')

    @expose('skylines.templates.upload.result')
    def do(self, file):
        user = request.identity['user']

        flights = []

        for name, f in IterateFiles(file.filename, file.file):
            filename = files.sanitise_filename(name)
            filename = files.add_file(filename, f)

            flight = Flight()
            flight.owner = request.identity['user']
            flight.filename = filename
            flight.club_id = user.club_id

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
