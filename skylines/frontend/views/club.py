from flask import Blueprint, g, request, jsonify

from skylines.database import db
from skylines.lib.dbutil import get_requested_record
from skylines.model import Club
from skylines.schemas import ClubSchema, ValidationError

club_blueprint = Blueprint('club', 'skylines')


@club_blueprint.route('/clubs/<club_id>', strict_slashes=False)
def read(club_id):
    club = get_requested_record(Club, club_id)

    json = ClubSchema().dump(club).data
    json['isWritable'] = club.is_writable(g.current_user)

    return jsonify(**json)


@club_blueprint.route('/clubs/<club_id>', methods=['POST'], strict_slashes=False)
def update(club_id):
    club = get_requested_record(Club, club_id)

    json = request.get_json()
    if json is None:
        return jsonify(error='invalid-request'), 400

    try:
        data = ClubSchema(partial=True).load(json).data
    except ValidationError, e:
        return jsonify(error='validation-failed', fields=e.messages), 422

    if 'name' in data:
        name = data.get('name')

        if name != club.name and Club.exists(name=name):
            return jsonify(error='duplicate-club-name'), 422

        club.name = name

    if 'website' in data:
        club.website = data.get('website')

    db.session.commit()

    return jsonify()
