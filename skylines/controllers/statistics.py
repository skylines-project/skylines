# -*- coding: utf-8 -*-

from tg import expose
from sqlalchemy.sql.expression import desc, or_, and_, between
from sqlalchemy import func, distinct
from skylines.lib.base import BaseController
from skylines.model import DBSession, User, Club, Flight


class StatisticsController(BaseController):
    @expose('skylines.templates.statistics.years')
    def index(self, **kw):
        query = DBSession.query(Flight.year.label('year'),
                                func.count('*').label('flights'),
                                func.count(distinct(Flight.pilot_id)).label('pilots'),
                                func.sum(Flight.olc_classic_distance).label('distance'),
                                func.sum(Flight.duration).label('duration')) \
                         .group_by(Flight.year).order_by(Flight.year.desc())

        max_flights = 1
        max_pilots = 1
        max_distance = 1
        max_duration = 1

        list = []
        for row in query:
            list.append(row)

            max_flights = max(max_flights, row.flights)
            max_pilots = max(max_pilots, row.pilots)
            max_distance = max(max_distance, row.distance)
            max_duration = max(max_duration, row.duration.total_seconds())

        return dict(years = list,
                    max_flights = max_flights,
                    max_pilots = max_pilots,
                    max_distance = max_distance,
                    max_duration = max_duration)

    @expose('skylines.templates.flights.top_pilots')
    def top(self):
        subq = DBSession.query(Flight.pilot_id,
                               func.count('*').label('count'),
                               func.sum(Flight.olc_plus_score).label('total')) \
               .group_by(Flight.pilot_id).subquery()
        result = DBSession.query(User, subq.c.count, subq.c.total) \
                 .join((subq, subq.c.pilot_id == User.user_id))
        result = result.order_by(desc('total'))
        result = result.limit(20)
        return dict(tab='top', result=result)

    @expose('skylines.templates.flights.top_clubs')
    def top_clubs(self):
        subq = DBSession.query(Flight.club_id,
                               func.count('*').label('count'),
                               func.sum(Flight.olc_plus_score).label('total')) \
               .group_by(Flight.club_id).subquery()
        result = DBSession.query(Club, subq.c.count, subq.c.total) \
                 .join((subq, subq.c.club_id == Club.id))
        result = result.order_by(desc('total'))
        result = result.limit(20)
        return dict(tab='top_clubs', result=result)
