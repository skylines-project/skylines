from datetime import date
from tg import expose, redirect
from tg.decorators import paginate, without_trailing_slash
from webob.exc import HTTPBadRequest
from sqlalchemy.sql.expression import desc, over
from sqlalchemy import func
from skylines.controllers.base import BaseController
from skylines.model import DBSession, User, Club, Flight, Airport

__all__ = ['RankingController']


class RankingController(BaseController):
    @expose()
    def index(self, **kw):
        redirect('/ranking/clubs')

    @staticmethod
    def __get_result(model, flight_field, **kw):
        subq = DBSession.query(getattr(Flight, flight_field),
                               func.count('*').label('count'),
                               func.sum(Flight.index_score).label('total')) \
               .group_by(getattr(Flight, flight_field)) \
               .outerjoin(Flight.model)

        if 'year' in kw:
            try:
                year = int(kw['year'])
            except:
                raise HTTPBadRequest

            year_start = date(year, 1, 1)
            year_end = date(year, 12, 31)
            subq = subq.filter(Flight.date_local >= year_start) \
                       .filter(Flight.date_local <= year_end)

        subq = subq.subquery()

        result = DBSession.query(model, subq.c.count, subq.c.total,
                                 over(func.rank(),
                                      order_by=desc('total')).label('rank')) \
                 .join((subq, getattr(subq.c, flight_field) == model.id))

        result = result.order_by(desc('total'))
        return result

    @without_trailing_slash
    @expose('skylines.templates.ranking.pilots')
    @paginate('result', items_per_page=20)
    def pilots(self, **kw):
        return dict(tab='pilots',
                    result=self.__get_result(User, 'pilot_id', **kw))

    @without_trailing_slash
    @expose('skylines.templates.ranking.clubs')
    @paginate('result', items_per_page=20)
    def clubs(self, **kw):
        return dict(tab='clubs',
                    result=self.__get_result(Club, 'club_id', **kw))

    @without_trailing_slash
    @expose('skylines.templates.ranking.airports')
    @paginate('result', items_per_page=20)
    def airports(self, **kw):
        return dict(tab='airports',
                    result=self.__get_result(Airport, 'takeoff_airport_id', **kw))
