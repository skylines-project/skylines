from tg import expose, redirect
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
        result = result.limit(20)
        return result

    @expose('skylines.templates.ranking.pilots')
    def pilots(self, **kw):
        return dict(tab='pilots',
                    result=self.__get_result(User, 'pilot_id'))

    @expose('skylines.templates.ranking.clubs')
    def clubs(self, **kw):
        return dict(tab='clubs',
                    result=self.__get_result(Club, 'club_id'))

    @expose('skylines.templates.ranking.airports')
    def airports(self, **kw):
        return dict(tab='airports',
                    result=self.__get_result(Airport, 'takeoff_airport_id'))
