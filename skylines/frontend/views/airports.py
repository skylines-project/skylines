from flask import Blueprint

from skylines.api.json import jsonify
from skylines.lib.dbutil import get_requested_record
from skylines.model import Airport

airports_blueprint = Blueprint('airports', 'skylines')


@airports_blueprint.route('/airports/<int:airport_id>')
def index(airport_id):
    airport = get_requested_record(Airport, airport_id)

    json = {
        'id': airport.id,
        'name': unicode(airport),
        'countryCode': airport.country_code,
    }

    return jsonify(json)
