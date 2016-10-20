from flask import Blueprint, g, request, jsonify

from skylines.database import db
from skylines.frontend.ember import send_index
from skylines.lib.dbutil import get_requested_record
from skylines.lib.vary import vary
from skylines.model import Club
from skylines.schemas import ClubSchema, ValidationError

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
        return send_index()

    json = ClubSchema().dump(g.club).data
    json['isWritable'] = g.club.is_writable(g.current_user)

    return jsonify(**json)


@club_blueprint.route('/pilots')
def pilots():
    return send_index()


@club_blueprint.route('/edit')
def edit():
    return send_index()


@club_blueprint.route('/', methods=['POST'])
def edit_post():
    json = request.get_json()
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = ClubSchema(partial=True).load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    if 'name' in data:
        name = data.get('name')

        if name != g.club.name and Club.exists(name=name):
            return jsonify(error='duplicate-club-name'), 422

        g.club.name = name

    if 'website' in data:
        g.club.website = data.get('website')

    db.session.commit()

    return jsonify()
