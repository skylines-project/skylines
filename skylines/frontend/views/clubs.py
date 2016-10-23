from flask import Blueprint, request, jsonify
from sqlalchemy import func

from skylines.frontend.ember import send_index
from skylines.model import Club
from skylines.lib.vary import vary
from skylines.schemas import ClubSchema

clubs_blueprint = Blueprint('clubs', 'skylines')


@clubs_blueprint.route('/clubs/')
@clubs_blueprint.route('/clubs/<path:path>')
def html(**kwargs):
    return send_index()


@clubs_blueprint.route('/api/clubs/')
def list():
    clubs = Club.query().order_by(func.lower(Club.name))

    name_filter = request.args.get('name')
    if name_filter:
        clubs = clubs.filter_by(name=name_filter)

    return jsonify(clubs=ClubSchema(only=('id', 'name')).dump(clubs, many=True).data)
