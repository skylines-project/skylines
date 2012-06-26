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
