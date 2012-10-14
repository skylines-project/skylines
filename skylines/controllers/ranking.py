from tg import expose, redirect
from tg.decorators import paginate, without_trailing_slash
from sqlalchemy.sql.expression import desc, over
from sqlalchemy import func
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Club, Flight, Airport

__all__ = ['RankingController']


class RankingController(BaseController):
    @expose()
    def index(self, **kw):
        redirect('/ranking/clubs')

    @staticmethod
    def __get_result(model, flight_field):
        subq = DBSession.query(getattr(Flight, flight_field),
                               func.count('*').label('count'),
                               func.sum(Flight.olc_plus_score).label('total')) \
               .group_by(getattr(Flight, flight_field)).subquery()

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
                    result=self.__get_result(User, 'pilot_id'))

    @without_trailing_slash
    @expose('skylines.templates.ranking.clubs')
    @paginate('result', items_per_page=20)
    def clubs(self, **kw):
        return dict(tab='clubs',
                    result=self.__get_result(Club, 'club_id'))

    @without_trailing_slash
    @expose('skylines.templates.ranking.airports')
    @paginate('result', items_per_page=20)
    def airports(self, **kw):
        return dict(tab='airports',
                    result=self.__get_result(Airport, 'takeoff_airport_id'))
