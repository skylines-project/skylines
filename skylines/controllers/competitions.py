from formencode import Invalid
from tg import expose, request, redirect
from tg.i18n import ugettext as _
from tg.decorators import with_trailing_slash, without_trailing_slash
from webob.exc import HTTPForbidden

from sqlalchemy.orm import joinedload

from .base import BaseController
from skylines.model import DBSession, Competition
from skylines.forms.competition import NewForm
from skylines.lib.formatter import format_date
from skylines.lib.dbutil import get_requested_record


class CompetitionController(BaseController):
    def __init__(self, competition):
        self.competition = competition

    @with_trailing_slash
    @expose('competitions/details.jinja')
    def index(self, **kw):
        return dict(competition=self.competition)


class CompetitionsController(BaseController):
    new_form = NewForm(DBSession)

    @expose()
    def _lookup(self, id, *remainder):
        competition = get_requested_record(Competition, id)
        controller = CompetitionController(competition)
        return controller, remainder

    @with_trailing_slash
    @expose('competitions/list.jinja')
    def index(self, **kw):
        query = DBSession.query(Competition) \
            .options(joinedload(Competition.airport))

        competitions = [{
            'id': competition.id,
            'name': competition.name,
            'location': competition.location_string,
            'start_date': format_date(competition.start_date),
            'end_date': format_date(competition.end_date),
        } for competition in query]

        return dict(competitions=competitions)

    @without_trailing_slash
    @expose('generic/form.jinja')
    def new(self, **kw):
        if not request.identity:
            raise HTTPForbidden

        if request.method.upper() == 'POST':
            self.new_post(**kw)

        return dict(title=_('Create a new competition'), form=self.new_form,
                    active_page='competitions')

    def new_post(self, **kw):
        try:
            self.new_form.validate(kw)
        except Invalid:
            return

        current_user = request.identity['user']

        competition = Competition(name=kw['name'])
        competition.creator = current_user
        competition.start_date = kw['start_date']
        competition.end_date = kw['end_date']

        DBSession.add(competition)
        DBSession.flush()

        redirect(str(competition.id))
