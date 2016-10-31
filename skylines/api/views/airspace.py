from flask import Blueprint, request

from skylines import api
from skylines.api.args import parse_location
from skylines.api.json import jsonify

airspace_blueprint = Blueprint('airspace', 'skylines')


@airspace_blueprint.route('/airspace', strict_slashes=False)
def list():
    location = parse_location(request.args)
    return jsonify(api.get_airspaces_by_location(location))
