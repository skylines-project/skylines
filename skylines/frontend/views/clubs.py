from flask import Blueprint, request, jsonify
from sqlalchemy import func

from skylines.model import Club
from skylines.schemas import ClubSchema

clubs_blueprint = Blueprint('clubs', 'skylines')


@clubs_blueprint.route('/api/clubs/', strict_slashes=False)
def list():
    clubs = Club.query().order_by(func.lower(Club.name))

    name_filter = request.args.get('name')
    if name_filter:
        clubs = clubs.filter_by(name=name_filter)

    return jsonify(clubs=ClubSchema(only=('id', 'name')).dump(clubs, many=True).data)
