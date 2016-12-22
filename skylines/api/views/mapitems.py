from flask import Blueprint, request

from skylines.api.json import jsonify
from skylines.api.args import parse_location
from skylines.api.schemas import airspace_list_schema, wave_list_schema
from skylines.model import Airspace, MountainWaveProject

mapitems_blueprint = Blueprint('mapitems', 'skylines')


@mapitems_blueprint.route('/mapitems', strict_slashes=False)
def list():
    location = parse_location(request.args)

    airspaces = airspace_list_schema.dump(Airspace.by_location(location).all(), many=True).data
    waves = wave_list_schema.dump(MountainWaveProject.by_location(location), many=True).data

    return jsonify(airspaces=airspaces, waves=waves)
