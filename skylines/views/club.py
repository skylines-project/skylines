from flask import Blueprint, render_template, g, redirect, url_for, abort
from sqlalchemy import func

from skylines import db
from skylines.forms import EditClubForm, CreateClubPilotForm
from skylines.lib.dbutil import get_requested_record
from skylines.model import User, Group, Club

club_blueprint = Blueprint('club', 'skylines')


@club_blueprint.url_value_preprocessor
def _pull_user_id(endpoint, values):
    g.club_id = values.pop('club_id')
    g.club = get_requested_record(Club, g.club_id)


@club_blueprint.url_defaults
def _add_user_id(endpoint, values):
    if hasattr(g, 'club_id'):
        values.setdefault('club_id', g.club_id)


@club_blueprint.route('/')
def index():
    return render_template(
        'clubs/view.jinja', active_page='settings', club=g.club)


@club_blueprint.route('/pilots')
def pilots():
    users = User.query(club=g.club).order_by(func.lower(User.name))

    return render_template(
        'clubs/pilots.jinja', active_page='settings',
        club=g.club, users=users)


@club_blueprint.route('/edit', methods=['GET', 'POST'])
def edit():
    if not g.club.is_writable(g.current_user):
        abort(403)

    form = EditClubForm(obj=g.club)
    if form.validate_on_submit():
        return edit_post(form)

    return render_template('clubs/edit.jinja', form=form)


def edit_post(form):
    g.club.name = form.name.data
    g.club.website = form.website.data
    db.session.commit()

    return redirect(url_for('.index'))


@club_blueprint.route('/create_pilot', methods=['GET', 'POST'])
def create_pilot():
    if not g.club.is_writable(g.current_user):
        abort(403)

    form = CreateClubPilotForm()
    if form.validate_on_submit():
        return create_pilot_post(form)

    return render_template('clubs/create_pilot.jinja', form=form)


def create_pilot_post(form):
    pilot = User(
        name=form.name.data,
        email_address=form.email_address.data,
        club=g.club
    )

    db.session.add(pilot)

    pilots = Group.query(group_name='pilots').first()
    if pilots:
        pilots.users.append(pilot)

    db.session.commit()

    return redirect(url_for('.pilots'))
