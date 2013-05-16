from datetime import date

from tg import expose, redirect
from tg.decorators import paginate, without_trailing_slash
from webob.exc import HTTPBadRequest
from sqlalchemy.sql.expression import desc, over
from sqlalchemy import func

from .base import BaseController
from skylines.model import DBSession, User, Club, Flight, Airport

__all__ = ['RankingController']


class RankingController(BaseController):
    @expose()
    def index(self, **kw):
        redirect('/ranking/clubs')

    @staticmethod
    def __get_result(model, flight_field, year=None):
        subq = DBSession \
            .query(getattr(Flight, flight_field),
                   func.count('*').label('count'),
                   func.sum(Flight.index_score).label('total')) \
            .group_by(getattr(Flight, flight_field)) \
            .outerjoin(Flight.model)

        if year:
            year_start = date(year, 1, 1)
            year_end = date(year, 12, 31)
            subq = subq.filter(Flight.date_local >= year_start) \
                       .filter(Flight.date_local <= year_end)

        subq = subq.subquery()

        result = DBSession \
            .query(model, subq.c.count, subq.c.total,
                   over(func.rank(), order_by=desc('total')).label('rank')) \
            .join((subq, getattr(subq.c, flight_field) == model.id))

        result = result.order_by(desc('total'))
        return result

    @staticmethod
    def __parse_year(**kw):
        try:
            return int(kw['year'])
        except:
            return None

    @without_trailing_slash
    @expose('ranking/pilots.jinja')
    @paginate('result', items_per_page=20)
    def pilots(self, **kw):
        year = self.__parse_year(**kw)
        return dict(active_header_tab='pilots', year=year,
                    result=self.__get_result(User, 'pilot_id', year=year))

    @without_trailing_slash
    @expose('ranking/clubs.jinja')
    @paginate('result', items_per_page=20)
    def clubs(self, **kw):
        year = self.__parse_year(**kw)
        return dict(active_header_tab='clubs', year=year,
                    result=self.__get_result(Club, 'club_id', year=year))

    @without_trailing_slash
    @expose('ranking/airports.jinja')
    @paginate('result', items_per_page=20)
    def airports(self, **kw):
        year = self.__parse_year(**kw)
        return dict(active_header_tab='airports', year=year,
                    result=self.__get_result(Airport, 'takeoff_airport_id', year=year))
