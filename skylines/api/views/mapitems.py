from flask import Blueprint, request

from skylines.api.json import jsonify
from skylines.api.args import parse_location
from skylines.schemas import AirspaceSchema, WaveSchema
from skylines.model import Airspace, MountainWaveProject

mapitems_blueprint = Blueprint("mapitems", "skylines")

airspace_list_schema = AirspaceSchema(
    only=("name", "_class", "top", "base", "countryCode")
)
wave_list_schema = WaveSchema()


@mapitems_blueprint.route("/mapitems", strict_slashes=False)
def _list():
    location = parse_location(request.args)

    airspaces = airspace_list_schema.dump(
        Airspace.by_location(location).all(), many=True
    ).data
    waves = wave_list_schema.dump(
        MountainWaveProject.by_location(location), many=True
    ).data

    return jsonify(airspaces=airspaces, waves=waves)
