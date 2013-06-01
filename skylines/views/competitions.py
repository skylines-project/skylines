from flask import Blueprint, render_template, request, redirect, url_for
from flask.ext.babel import _
from sqlalchemy.orm import joinedload

from skylines.model import DBSession, Competition
from skylines.forms.competition import NewForm
from skylines.lib.formatter import format_date
from skylines.lib.decorators import validate, login_required

competitions_blueprint = Blueprint('competitions', 'skylines')

# Forms
new_form = NewForm(DBSession)


@competitions_blueprint.route('/')
def index():
    query = DBSession.query(Competition) \
        .options(joinedload(Competition.airport))

    competitions = [{
        'id': competition.id,
        'name': competition.name,
        'location': competition.location_string,
        'start_date': format_date(competition.start_date),
        'end_date': format_date(competition.end_date),
    } for competition in query]

    return render_template(
        'competitions/list.jinja',
        competitions=competitions)


@competitions_blueprint.route('/new')
@login_required()
def new():
    return render_template(
        'generic/form.jinja', title=_('Create a new competition'),
        form=new_form, active_page='competitions')


@competitions_blueprint.route('/new', methods=['POST'])
@login_required()
@validate(new_form, new)
def new_post():
    current_user = request.identity['user']

    competition = Competition(name=request.form['name'])
    competition.creator = current_user
    competition.start_date = request.form['start_date']
    competition.end_date = request.form['end_date']

    DBSession.add(competition)
    DBSession.commit()

    return redirect(url_for('competition.index', competition_id=competition.id))
