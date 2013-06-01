from collections import namedtuple

from flask import Blueprint, render_template, g
from sqlalchemy.orm import joinedload, contains_eager

from skylines.model import Competition, CompetitionParticipation
from skylines.lib.dbutil import get_requested_record

competition_blueprint = Blueprint('competition', 'skylines')


@competition_blueprint.url_value_preprocessor
def _pull_flight_id(endpoint, values):
    g.competition_id = values.pop('competition_id')
    g.competition = get_requested_record(Competition, g.competition_id)


@competition_blueprint.url_defaults
def _add_flight_id(endpoint, values):
    if hasattr(g, 'competition_id'):
        values.setdefault('competition_id', g.competition_id)


@competition_blueprint.route('/')
def index():
    return render_template(
        'competitions/details.jinja',
        competition=g.competition)


@competition_blueprint.route('/participants')
def participants():
    pilots = CompetitionParticipation.query(competition=g.competition) \
        .join('user').options(contains_eager('user')) \
        .options(joinedload('class_')) \
        .order_by('tg_user.name')

    Admin = namedtuple('Admin', ['user'])
    admins = sorted(g.competition.admins, key=str)
    admins = [Admin(user) for user in admins]

    return render_template(
        'competitions/participants.jinja',
        competition=g.competition,
        pilots=pilots, admins=admins)
