# -*- coding: utf-8 -*-

from tg import expose, request
from webob.exc import HTTPNotFound
from sqlalchemy.sql.expression import desc, or_, and_, between
from sqlalchemy import func, distinct
from skylines.lib.base import BaseController
from skylines.lib.dbutil import get_requested_record
from skylines.model import DBSession, User, Club, Flight, Airport


class StatisticsController(BaseController):
    @expose('skylines.templates.statistics.years')
    def _default(self, *args, **kw):
        club = None
        pilot = None
        selected_club = None
        selected_pilot = None
        airport = None

        if args and len(args) >= 2:
            if args[0] == 'pilot':
                selected_pilot = get_requested_record(User, args[1])

            if args[0] == 'club':
                selected_club = get_requested_record(Club, args[1])

            if args[0] == 'airport':
                airport = get_requested_record(Airport, args[1])

        if request.identity:
            pilot = request.identity['user']
            club = request.identity['user'].club

        query = DBSession.query(Flight.year.label('year'),
                                func.count('*').label('flights'),
                                func.count(distinct(Flight.pilot_id)).label('pilots'),
                                func.sum(Flight.olc_classic_distance).label('distance'),
                                func.sum(Flight.duration).label('duration'))

        if selected_pilot:
            query = query.filter(Flight.pilot_id == selected_pilot.id)

        if selected_club:
            query = query.filter(Flight.club_id == selected_club.id)

        if airport:
            query = query.filter(Flight.takeoff_airport_id == airport.id)

        query = query.group_by(Flight.year).order_by(Flight.year.desc())

        max_flights = 1
        max_pilots = 1
        max_distance = 1
        max_duration = 1

        sum_flights = 0
        sum_distance = 0
        sum_duration = 0

        list = []
        for row in query:
            list.append(row)

            max_flights = max(max_flights, row.flights)
            max_pilots = max(max_pilots, row.pilots)
            max_distance = max(max_distance, row.distance)
            max_duration = max(max_duration, row.duration.total_seconds())

            sum_flights = sum_flights + row.flights
            sum_distance = sum_distance + row.distance
            sum_duration = sum_duration + row.duration.total_seconds()

        return dict(years = list,
                    max_flights = max_flights,
                    max_pilots = max_pilots,
                    max_distance = max_distance,
                    max_duration = max_duration,
                    sum_flights = sum_flights,
                    sum_distance = sum_distance,
                    sum_duration = sum_duration,
                    airport = airport,
                    pilot = pilot,
                    club = club,
                    selected_pilot = selected_pilot,
                    selected_club = selected_club)
