from flask import Blueprint, request
from sqlalchemy import func

from skylines.api.json import jsonify
from skylines.database import db
from skylines.api.oauth import oauth
from skylines.lib.dbutil import get_requested_record
from skylines.model import Club, User
from skylines.schemas import ClubSchema, ValidationError

clubs_blueprint = Blueprint('clubs', 'skylines')


@clubs_blueprint.route('/clubs', strict_slashes=False)
def list():
    clubs = Club.query().order_by(func.lower(Club.name))

    name_filter = request.args.get('name')
    if name_filter:
        clubs = clubs.filter_by(name=name_filter)

    return jsonify(clubs=ClubSchema(only=('id', 'name')).dump(clubs, many=True).data)


@clubs_blueprint.route('/clubs/<club_id>', strict_slashes=False)
@oauth.optional()
def read(club_id):
    current_user = User.get(request.user_id) if request.user_id else None

    club = get_requested_record(Club, club_id)

    json = ClubSchema().dump(club).data
    json['isWritable'] = club.is_writable(current_user)

    return jsonify(json)


@clubs_blueprint.route('/clubs/<club_id>', methods=['POST'], strict_slashes=False)
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
