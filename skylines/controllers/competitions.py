from tg import expose
from tg.decorators import with_trailing_slash

from sqlalchemy.orm import joinedload

from .base import BaseController
from skylines.model import DBSession, Competition


class CompetitionsController(BaseController):
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
