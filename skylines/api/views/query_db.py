import sys

from datetime import date

from flask import Blueprint, request, g
from sqlalchemy import func, distinct, text
from sqlalchemy.sql.expression import desc, over
from sqlalchemy.orm import eagerload

from skylines.api.json import jsonify
from skylines.database import db
from skylines.model import User, Club, Flight, Airport
from skylines.lib.table_tools import Pager, Sorter
from skylines.schemas import AirportSchema, ClubSchema, UserSchema


def _get_result_Flight(table, table_column, year=None):
    subq = (
        db.session.query(
            getattr(Flight, table_column),
            func.count("*").label("count"),
            func.sum(Flight.index_score).label("total"),
        )
        .group_by(getattr(Flight, table_column))
        .outerjoin(Flight.model)  #glider model
        .filter(Flight.is_rankable())
    )

    if isinstance(year, int):
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        subq = subq.filter(Flight.date_local >= year_start).filter(
            Flight.date_local <= year_end
        )

    subq = subq.subquery()

    result = db.session.query(
        table,
        subq.c.count,
        subq.c.total,
        over(func.rank(), order_by=desc("total")).label("rank"),
    ).join((subq, getattr(subq.c, table_column) == table.id))

    if table == User:
        result = result.outerjoin(table.club)
        result = result.options(eagerload(table.club))

    return result

def _handle_request_rank(table, table_column):
    current_year = date.today().year
    year = _parse_year()
    result = _get_result_Flight(table, table_column, year=year)

    result = Sorter.sort(
        result,
        "sorter",
        "rank",
        valid_columns={"rank": "rank", "count": "count", "total": "total"},
        default_order="asc",
    )
    result = Pager.paginate(result, "result")
    return dict(year=year, current_year=current_year, result=result)

def _parse_year():
    try:
        year = request.args["year"]

        if year == "all":
            return "all"

        return int(year)
    except:
        current_year = date.today().year
        return current_year


def group_by(pilot_id):
    pass


def _get_result_Flight_User_byClub(year=None):
    '''return the number of users in flights that are recorded under the club id.
    Rankable flight means public flight.
    Sort by number of flights this year'''

    query = db.session.query( \
        Flight.club_id, \
        func.count((Flight.pilot_id.distinct())).label('users_count') \
        , func.count(Flight.id).label('flights_count')) \
        .group_by(Flight.club_id)

    if isinstance(year, int): # if year is None, then get flights for all seasons
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        query = query.filter(Flight.date_local >= year_start)\
            .filter(Flight.date_local <= year_end)

    subq = query.subquery()

    result = db.session.query(
        Club,
        subq.c.flights_count,
        subq.c.users_count,
        over(func.rank(), order_by=desc("flights_count")).label("rank"),
    ).join((subq, getattr(subq.c, "club_id") == Club.id))

    return result

def _handle_request_flight_user_byClub():
    current_year = date.today().year
    year = _parse_year()
    result = _get_result_Flight_User_byClub(year=year)

    result = Sorter.sort(
        result,
        "sorter",
        "flights",
        valid_columns={"flights": "flights_count", "users": "users_count", "rank": "rank"},
        default_order="desc",
    )

    result = Pager.paginate(result, "result")
    return dict(year=year, current_year=current_year, result=result)


def _get_result_Groupflight_User_byClub(year=None):
    '''return the number of users in flights that are recorded under the club id.
    Rankable flight means public flight.
    Sort by number of flights this year'''

    query = db.session.query( \
        Flight.club_id, \
        func.count((Flight.pilot_id.distinct())).label('users_count') \
        , func.count(Flight.id).label('flights_count')) \
        .group_by(Flight.club_id)

    if isinstance(year, int): # if year is None, then get flights for all seasons
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        query = query.filter(Flight.date_local >= year_start)\
            .filter(Flight.date_local <= year_end)

    subq = query.subquery()

    result = db.session.query(
        Club,
        subq.c.flights_count,
        subq.c.users_count,
        over(func.rank(), order_by=desc("flights_count")).label("rank"),
    ).join((subq, getattr(subq.c, "club_id") == Club.id))

    return result

def _handle_request_flight_user_byClub():
    current_year = date.today().year
    year = _parse_year()
    result = _get_result_Flight_User_byClub(year=year)

    result = Sorter.sort(
        result,
        "sorter",
        "flights",
        valid_columns={"flights": "flights_count", "users": "users_count", "rank": "rank"},
        default_order="desc",
    )

    result = Pager.paginate(result, "result")
    return dict(year=year, current_year=current_year, result=result)
