from datetime import date

from flask import Blueprint, request, redirect, url_for, render_template, jsonify, g
from sqlalchemy import func
from sqlalchemy.sql.expression import desc, over
from sqlalchemy.orm import eagerload

from skylines.database import db
from skylines.model import User, Club, Flight, Airport
from skylines.lib.table_tools import Pager, Sorter
from skylines.lib.vary import vary

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
@vary('accept')
def pilots():
    data = _handle_request(User, 'pilot_id')

    if 'application/json' in request.headers.get('Accept', ''):
        json = []
        for pilot, count, total, rank in data['result']:
            row = {
                'rank': rank,
                'flights': count,
                'points': total,
                'user': {
                    'id': pilot.id,
                    'name': unicode(pilot),
                },
            }

            if pilot.club_id:
                row['club'] = {
                    'id': pilot.club_id,
                    'name': unicode(pilot.club),
                }

            json.append(row)

        return jsonify(ranking=json, total=g.paginators['result'].count)

    return render_template('ember-page.jinja', active_page='ranking')


@ranking_blueprint.route('/clubs')
@vary('accept')
def clubs():
    data = _handle_request(Club, 'club_id')

    if 'application/json' in request.headers.get('Accept', ''):
        json = []
        for club, count, total, rank in data['result']:
            row = {
                'rank': rank,
                'flights': count,
                'points': total,
                'club': {
                    'id': club.id,
                    'name': unicode(club),
                },
            }

            json.append(row)

        return jsonify(ranking=json, total=g.paginators['result'].count)

    return render_template('ember-page.jinja', active_page='ranking')


@ranking_blueprint.route('/airports')
@vary('accept')
def airports():
    data = _handle_request(Airport, 'takeoff_airport_id')

    if 'application/json' in request.headers.get('Accept', ''):
        json = []
        for airport, count, total, rank in data['result']:
            row = {
                'rank': rank,
                'flights': count,
                'points': total,
                'airport': {
                    'id': airport.id,
                    'name': unicode(airport),
                    'countryCode': airport.country_code,
                },
            }

            json.append(row)

        return jsonify(ranking=json, total=g.paginators['result'].count)

    return render_template('ember-page.jinja', active_page='ranking')
