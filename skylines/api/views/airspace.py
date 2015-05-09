from flask import Blueprint, request

from skylines import api
from .json import jsonify
from .parser import parse_location

airspace_blueprint = Blueprint('airspace', 'skylines')


@airspace_blueprint.route('/airspace/')
@airspace_blueprint.route('/airspace', endpoint='list')
def _list():
    location = parse_location(request.args)
    return jsonify(api.get_airspaces_by_location(location))
