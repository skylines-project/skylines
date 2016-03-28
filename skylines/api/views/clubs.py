from flask import Blueprint
from werkzeug.exceptions import NotFound

from skylines.api.schemas import ClubSchema
from skylines.model import Club
from skylines.api.views.json import jsonify

clubs_blueprint = Blueprint('clubs', 'skylines')
club_schema = ClubSchema()


@clubs_blueprint.route('/clubs/<int:club_id>')
def read(club_id):
    club = Club.get(club_id)
    if club is None:
        raise NotFound()

    result = club_schema.dump(club)
    return jsonify(result.data)
