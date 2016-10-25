from flask import Blueprint, jsonify

from skylines.lib.dbutil import get_requested_record
from skylines.model import Airport

airport_blueprint = Blueprint('airport', 'skylines')


@airport_blueprint.route('/airports/<int:airport_id>')
def index(airport_id):
    airport = get_requested_record(Airport, airport_id)

    json = {
        'id': airport.id,
        'name': unicode(airport),
        'countryCode': airport.country_code,
    }

    return jsonify(**json)
