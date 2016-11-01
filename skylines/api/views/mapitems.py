from flask import Blueprint, request

from skylines import api
from skylines.api.json import jsonify
from skylines.api.args import parse_location

mapitems_blueprint = Blueprint('mapitems', 'skylines')


@mapitems_blueprint.route('/mapitems', strict_slashes=False)
def list():
    location = parse_location(request.args)
    return jsonify({
        'airspaces': api.get_airspaces_by_location(location),
        'waves': api.get_waves_by_location(location),
    })
