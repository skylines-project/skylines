from flask import Blueprint, render_template, g
from sqlalchemy import func

from skylines.forms import club, pilot as pilot_forms
from skylines.lib.dbutil import get_requested_record
from skylines.model import DBSession, User, Group, Club

club_blueprint = Blueprint('club', 'skylines')


@club_blueprint.url_value_preprocessor
def _pull_user_id(endpoint, values):
    g.club_id = values.pop('club_id')
    g.club = get_requested_record(Club, g.club_id)


@club_blueprint.url_defaults
def _add_user_id(endpoint, values):
    values.setdefault('club_id', g.club_id)


@club_blueprint.route('/')
def index():
    return render_template(
        'clubs/view.jinja', active_page='settings', club=g.club)
