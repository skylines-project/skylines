from tg import expose, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from skylines.lib.base import BaseController
from skylines import files
from skylines.model import DBSession, Flight
from skylines.lib.analysis import analyse_flight

class UploadController(BaseController):
    allow_only = has_permission('upload',
                                msg=l_("You don't have permission to upload flights."))

    @expose('skylines.templates.upload.index')
    def index(self):
        return dict(page = 'upload')

    @expose()
    def do(self, file):
        user = request.identity['user']

        filename = files.sanitise_filename(file.filename)
        filename = files.add_file(filename, file.file)

        flight = Flight()
        flight.owner = request.identity['user']
        flight.filename = filename
        flight.club_id = user.club_id

        analyse_flight(flight)

        DBSession.add(flight)
        DBSession.flush()

        return redirect('/flights/unassigned')

