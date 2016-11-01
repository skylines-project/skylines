from flask import Blueprint

from skylines.api.json import jsonify
from skylines.lib.dbutil import get_requested_record
from skylines.model import Airport
from skylines.schemas import AirportSchema

airports_blueprint = Blueprint('airports', 'skylines')


@airports_blueprint.route('/airports/<int:airport_id>')
def index(airport_id):
    airport = get_requested_record(Airport, airport_id)
    return jsonify(AirportSchema().dump(airport).data)
