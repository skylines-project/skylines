from tg import expose, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from skylines.lib.base import BaseController
from skylines import model, files
from skylines.lib.analysis import analyse_flight

class UploadController(BaseController):
    allow_only = has_permission('upload',
                                msg=l_("You don't have permission to upload flights."))

    @expose('skylines.templates.upload.index')
    def index(self):
        return dict(page = 'upload')

    @expose()
    def do(self, file):
        filename = files.sanitise_filename(file.filename)
        files.add_file(filename, file.file)

        flight = model.Flight()
        flight.owner = request.identity['user']
        flight.filename = filename

        analyse_flight(flight)

        model.DBSession.add(flight)
        model.DBSession.flush()

        return redirect('/flights/my')

