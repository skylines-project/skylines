from flask import Blueprint, request

from skylines import api
from .json import jsonify
from .parser import parse_location

mapitems_blueprint = Blueprint('mapitems', 'skylines')


@mapitems_blueprint.route('/mapitems/')
@mapitems_blueprint.route('/mapitems', endpoint='list')
def _list():
    location = parse_location(request.args)
    return jsonify({
        'airspaces': api.get_airspaces_by_location(location),
        'waves': api.get_waves_by_location(location),
    })
