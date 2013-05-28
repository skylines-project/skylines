from flask import Blueprint, render_template, g, request, redirect, url_for, abort
from flask.ext.babel import _
from sqlalchemy import func

from skylines.forms import club, pilot as pilot_forms
from skylines.lib.dbutil import get_requested_record
from skylines.lib.decorators import validate
from skylines.model import DBSession, User, Group, Club

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


@club_blueprint.route('/edit')
def edit():
    if not g.club.is_writable(request.identity):
        abort(403)

    return render_template(
        'generic/form.jinja', active_page='settings', title=_('Edit Club'),
        form=club.edit_form, values=g.club)


@club_blueprint.route('/edit', methods=['POST'])
@validate(club.edit_form, edit)
def edit_post():
    if not g.club.is_writable(request.identity):
        abort(403)

    g.club.name = request.form['name']
    g.club.website = request.form['website']
    DBSession.commit()

    return redirect(url_for('.index'))


@club_blueprint.route('/create_pilot')
def create_pilot():
    if not g.club.is_writable(request.identity):
        abort(403)

    return render_template(
        'generic/form.jinja', active_page='settings', title=_('Create Pilot'),
        form=pilot_forms.new_form, values={})


@club_blueprint.route('/create_pilot', methods=['POST'])
@validate(pilot_forms.new_form, create_pilot)
def create_pilot_post():
    if not g.club.is_writable(request.identity):
        abort(403)

    pilot = User(
        name=request.form['name'],
        email_address=request.form['email_address'],
        club=g.club
    )

    DBSession.add(pilot)

    pilots = Group.query(group_name='pilots').first()
    if pilots:
        pilots.users.append(pilot)

    DBSession.commit()

    return redirect(url_for('.pilots'))
