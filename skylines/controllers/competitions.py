from functools import partial

from tg import expose, validate, request, redirect
from tg.i18n import ugettext as _
from tg.decorators import with_trailing_slash, without_trailing_slash
from webob.exc import HTTPForbidden

from sqlalchemy.orm import joinedload

from .base import BaseController
from skylines.model import DBSession, Competition
from skylines.forms.competition import NewForm


class CompetitionsController(BaseController):
    new_form = NewForm(DBSession)

    @with_trailing_slash
    @expose('competitions/list.jinja')
    def index(self, **kw):
        query = DBSession.query(Competition) \
            .options(joinedload(Competition.airport))

        competitions = [{
            'name': competition.name,
            'location': competition.location_string,
            'date': competition.date_string,
        } for competition in query]

        return dict(competitions=competitions)

    @without_trailing_slash
    @expose('generic/form.jinja')
    def new(self, **kw):
        if not request.identity:
            raise HTTPForbidden

        new_form = partial(self.new_form, action='new_post')
        return dict(title=_('Create a new competition'), form=new_form)

    @expose()
    @validate(form=new_form, error_handler=new)
    def new_post(self, name, start_date, end_date, **kw):
        if not request.identity:
            raise HTTPForbidden

        current_user = request.identity['user']

        competition = Competition(name=name)
        competition.creator = current_user
        competition.start_date = start_date
        competition.end_date = end_date

        DBSession.add(competition)
        DBSession.flush()

        redirect('.')
