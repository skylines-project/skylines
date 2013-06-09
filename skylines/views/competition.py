from collections import namedtuple

from flask import Blueprint, render_template, g, request, abort, redirect, url_for
from sqlalchemy.orm import joinedload, contains_eager

from skylines import db
from skylines.model import Competition, CompetitionParticipation, User
from skylines.model.search import search_query, text_to_tokens, escape_tokens
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


@competition_blueprint.route('/admins/edit')
def admins_edit():
    if not g.competition.is_writable(g.current_user):
        abort(403)

    result = dict(competition=g.competition)

    search_text = request.values.get('search')
    if search_text:
        # Split the search text into tokens and escape them properly
        tokens = text_to_tokens(search_text)
        tokens = escape_tokens(tokens)

        # Create search query
        query = search_query(User, tokens)

        # Perform query and limit output to 20 items
        search_results = query.limit(20).all()

        def is_no_admin(user):
            return not any(map(lambda a: a.id == user.id, g.competition.admins))

        search_results = filter(is_no_admin, search_results)

        result['user_search_text'] = search_text
        result['user_search_results'] = search_results

    return render_template('competitions/edit_admins.jinja', **result)


@competition_blueprint.route('/admins/add/<int:user_id>')
def admins_add(user_id):
    if not g.competition.is_writable(g.current_user):
        abort(403)

    # Search the database for the user
    user = get_requested_record(User, user_id)

    # Promote the user to a competition admin
    g.competition.admins.append(user)
    db.session.commit()

    return redirect(request.args.get('next') or
                    url_for('competition.admins_edit'))


@competition_blueprint.route('/admins/remove/<int:user_id>')
def admins_remove(user_id):
    if not g.competition.is_writable(g.current_user):
        abort(403)

    # Search the database for the user
    user = get_requested_record(User, user_id)

    # Promote the user to a competition admin
    g.competition.admins.remove(user)
    db.session.commit()

    return redirect(request.args.get('next') or
                    url_for('competition.admins_edit'))
