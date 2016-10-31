from flask import Blueprint, request

from skylines import api
from skylines.api.args import parse_location
from skylines.api.json import jsonify

waves_blueprint = Blueprint('waves', 'skylines')


@waves_blueprint.route('/mountain_wave_project', strict_slashes=False)
def list():
    location = parse_location(request.args)
    return jsonify(api.get_waves_by_location(location))
