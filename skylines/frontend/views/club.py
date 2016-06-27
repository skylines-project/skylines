from flask import Blueprint, render_template, g, request, jsonify

from skylines.database import db
from skylines.lib.dbutil import get_requested_record
from skylines.lib.vary import vary
from skylines.model import Club

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
@vary('accept')
def index():
    if 'application/json' not in request.headers.get('Accept', ''):
        return render_template('ember-page.jinja', active_page='settings')

    json = {
        'id': g.club.id,
        'name': unicode(g.club),
        'timeCreated': g.club.time_created.isoformat(),
        'isWritable': g.club.is_writable(g.current_user),
    }

    if g.club.website:
        json['website'] = g.club.website

    if g.club.owner:
        json['owner'] = {
            'id': g.club.owner.id,
            'name': unicode(g.club.owner),
        }

    return jsonify(**json)


@club_blueprint.route('/pilots')
def pilots():
    return render_template('ember-page.jinja', active_page='settings')


@club_blueprint.route('/edit')
def edit():
    return render_template('ember-page.jinja', active_page='settings')


@club_blueprint.route('/', methods=['POST'])
def edit_post():
    json = request.get_json()
    if not json:
        return jsonify(error='invalid-request'), 400

    name = json.get('name')
    if name is not None:
        name = name.strip()

        if name == '':
            return jsonify(error='invalid-name'), 422

        if name != g.club.name and Club.exists(name=name):
            return jsonify(error='name-exists-already'), 422

        g.club.name = name

    website = json.get('website')
    if website is not None:
        website = website.strip()

        if website == '':
            return jsonify(error='invalid-first-name'), 422

        g.club.website = website

    db.session.commit()

    return jsonify()
