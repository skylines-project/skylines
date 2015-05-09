from datetime import date

from flask import Blueprint, request, redirect, url_for, render_template
from sqlalchemy import func
from sqlalchemy.sql.expression import desc, over
from sqlalchemy.orm import eagerload

from skylines.database import db
from skylines.model import User, Club, Flight, Airport
from skylines.lib.table_tools import Pager, Sorter

ranking_blueprint = Blueprint('ranking', 'skylines')


def _get_result(model, flight_field, year=None):
    subq = db.session \
        .query(getattr(Flight, flight_field),
               func.count('*').label('count'),
               func.sum(Flight.index_score).label('total')) \
        .group_by(getattr(Flight, flight_field)) \
        .outerjoin(Flight.model) \
        .filter(Flight.is_rankable())

    if isinstance(year, int):
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        subq = subq.filter(Flight.date_local >= year_start) \
                   .filter(Flight.date_local <= year_end)

    subq = subq.subquery()

    result = db.session \
        .query(model, subq.c.count, subq.c.total,
               over(func.rank(), order_by=desc('total')).label('rank')) \
        .join((subq, getattr(subq.c, flight_field) == model.id))

    if model == User:
        result = result.outerjoin(model.club)
        result = result.options(eagerload(model.club))

    return result


def _handle_request(model, flight_field):
    current_year = date.today().year
    year = _parse_year()
    result = _get_result(model, flight_field, year=year)

    result = Sorter.sort(result, 'sorter', 'rank',
                         valid_columns={'rank': 'rank',
                                        'count': 'count',
                                        'total': 'total'},
                         default_order='asc')
    result = Pager.paginate(result, 'result')
    return dict(year=year, current_year=current_year, result=result)


def _parse_year():
    try:
        year = request.args['year']

        if year == 'all':
            return 'all'

        return int(year)
    except:
        current_year = date.today().year
        return current_year


@ranking_blueprint.route('/')
def index():
    return redirect(url_for('ranking.clubs'))


@ranking_blueprint.route('/pilots')
def pilots():
    return render_template('ranking/pilots.jinja',
                           active_header_tab='pilots',
                           **_handle_request(User, 'pilot_id'))


@ranking_blueprint.route('/clubs')
def clubs():
    return render_template('ranking/clubs.jinja',
                           active_header_tab='clubs',
                           **_handle_request(Club, 'club_id'))


@ranking_blueprint.route('/airports')
def airports():
    return render_template('ranking/airports.jinja',
                           active_header_tab='airports',
                           **_handle_request(Airport, 'takeoff_airport_id'))
