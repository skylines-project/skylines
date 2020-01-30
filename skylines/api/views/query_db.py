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


def _get_result_Flight_User_byClub(year):
    '''return the number of users in flights that are recorded under the club id.
    Rankable flight means public flight.
    Sort by number of flights this year'''
    # query_flights = (
    #     db.session.query(Flight.
    #         func.count("*").label("flights_count"),
    #     )
    #     .group_by(getattr(Flight, "club_id"))
    # )

    # if isinstance(year, int):
    #     year_start = date(year, 1, 1)
    #     year_end = date(year, 12, 31)
    #     query_flights = query_flights.filter(Flight.date_local >= year_start).filter(
    #         Flight.date_local <= year_end
    #     )

    # subq_flights = query_flights.subquery()


    if isinstance(year, int):
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        query_flights_users = db.session.query(Flight.pilot_id).filter(Flight.date_local >= year_start).filter(
            Flight.date_local <= year_end).group_by(Flight.pilot_id).all()
        query_flights_counts = db.session.query(func.count(Flight.club_id),Flight.club_id).filter(Flight.date_local >= year_start).filter(
            Flight.date_local <= year_end
        ).group_by(Flight.club_id).all()

        query_flights_join_users_flights = db.session.query(Flight,User).join(User,Flight.pilot).all()

        query_flights_users_grouped = db.session.query(Flight.pilot_id,Flight.club_id).filter(Flight.date_local >= year_start).filter(
            Flight.date_local <= year_end).group_by(Flight.club_id,Flight.pilot_id).all()

        query_flights_users_distinct = db.session.query(func.count(distinct(Flight.pilot_id)),Flight.pilot_id).filter(Flight.date_local >= year_start).filter(
            Flight.date_local <= year_end
        ).group_by(Flight.pilot_id).all()

        query_flight_users_clubs = db.session.query(Flight.club_id).filter(Flight.date_local >= year_start).filter(
            Flight.date_local <= year_end).filter(Flight.club_id == User.club_id).group_by(Flight.club_id).all()

        query_flight_users_clubs = db.session.query(Flight.club_id).filter(Flight.date_local >= year_start).filter(
            Flight.date_local <= year_end).filter(Flight.club_id == User.club_id).group_by(Flight.club_id).all()

        query_flight_users_clubs_count = db.session.query(Flight.club_id,func.count(Flight.club_id)).filter(Flight.date_local >= year_start).filter(
            Flight.date_local <= year_end).filter(Flight.club_id == User.club_id).group_by(Flight.club_id).all() #gives a useless count.

        qu = db.session.query(User.club_id)
        qf = db.session.query(Flight.club_id).filter(Flight.date_local >= year_start).filter(
            Flight.date_local <= year_end).filter(Flight.club_id == User.club_id)

        qusers_with_flights = db.session.query(qu).join(qf,Flight.club_id==User.club_id)

        # query_flights_join_users_flights = db.session.query(Flight.pilot_id,User.club_id,Club).join(Club,Flight.club).\
        #     join(User,Flight.pilot).group_by(Flight.pilot_id,User.club_id).all()



        txtqueryUsers = db.session.query(User).from_statement(\
                      text("SELECT * from users where club_id=1")).params(name='ed').all()

        # txtqueryUsersFlightsClubs = db.session.query(Flight,User).from_statement(\
        #               text('''SELECT flights.club_id, users.first_name FROM flights
        #                        full join users on flights.club_id=users.club_id  '''))\
        #                 .params(name='ed').all()#INNER JOIN users on flights.club_id=users.club_id

    print query_flights_users
    print query_flights_counts
    print query_flights_join_users_flights
    print query_flights_users_grouped
    print query_flights_users_distinct
    print txtqueryUsers

    # txtqueryUsersFlightsClubs = db.session.query(Flight, User).from_statement( \
    #     text('''SELECT flights.club_id, users.first_name FROM flights
    #                        full join users on flights.club_id=users.club_id  ''')) \
    #     .params(name='ed').all()  # INNER JOIN users on flights.club_id=users.club_id

    # print txtqueryUsersFlightsClubs

    print query_flight_users_clubs
    print query_flight_users_clubs_count
    print qusers_with_flights

    # query_users = (,
    #     db.session.query(
    #         getattr(User, "club_id"),
    #         func.count("*").label("users_count"),
    #     )
    #         .group_by(getattr(User, "name"))
    # )
    #
    # subq_users = query_users.subquery()

    result = ''
    #
    # result = db.session.query(
    #     Club,
    #     subq_flights.c.flights_count,
    #     subq_users.c.users_count,
    # ).join((subq_flights, getattr(subq_flights.c, "club_id") == Club.id))

    return result


def _handle_request_flight_user_byClub():
    current_year = date.today().year
    year = _parse_year()
    result = _get_result_Flight_User_byClub(year=year)

    # result = Sorter.sort(
    #     result,
    #     "sorter",
    #     "flights",
    #     valid_columns={"flights": "flights_count", "users": "users_count"},
    #     default_order="desc",
    # )

    result = Pager.paginate(result, "result")
    return dict(year=year, current_year=current_year, result=result)
