from tg import expose, redirect
from sqlalchemy.sql.expression import desc, over
from sqlalchemy import func
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Club, Flight, Airport


class RankingController(BaseController):
    @expose()
    def index(self, **kw):
        redirect('/ranking/clubs')

    @expose('skylines.templates.ranking.pilots')
    def pilots(self, **kw):
        subq = DBSession.query(Flight.pilot_id,
                               func.count('*').label('count'),
                               func.sum(Flight.olc_plus_score).label('total')) \
               .group_by(Flight.pilot_id).subquery()
        result = DBSession.query(User, subq.c.count, subq.c.total,
                                 over(func.rank(),
                                      order_by=desc('total')).label('rank')) \
                 .join((subq, subq.c.pilot_id == User.id))
        result = result.order_by(desc('total'))
        result = result.limit(20)
        return dict(tab='pilots', result=result)

    @expose('skylines.templates.ranking.clubs')
    def clubs(self, **kw):
        subq = DBSession.query(Flight.club_id,
                               func.count('*').label('count'),
                               func.sum(Flight.olc_plus_score).label('total')) \
               .group_by(Flight.club_id).subquery()
        result = DBSession.query(Club, subq.c.count, subq.c.total,
                                 over(func.rank(),
                                      order_by=desc('total')).label('rank')) \
                 .join((subq, subq.c.club_id == Club.id))
        result = result.order_by(desc('total'))
        result = result.limit(20)
        return dict(tab='clubs', result=result)

    @expose('skylines.templates.ranking.airports')
    def airports(self, **kw):
        subq = DBSession.query(Flight.takeoff_airport_id,
                               func.count('*').label('count'),
                               func.sum(Flight.olc_plus_score).label('total')) \
               .group_by(Flight.takeoff_airport_id).subquery()
        result = DBSession.query(Airport, subq.c.count, subq.c.total,
                                 over(func.rank(),
                                      order_by=desc('total')).label('rank')) \
                 .join((subq, subq.c.takeoff_airport_id == Airport.id))
        result = result.order_by(desc('total'))
        result = result.limit(20)
        return dict(tab='airports', result=result)
