from flask import Blueprint

from skylines.api.json import jsonify
from skylines.model import AircraftModel
from skylines.schemas import AircraftModelSchema

aircraft_models_blueprint = Blueprint('aircraft_models', 'skylines')


@aircraft_models_blueprint.route('/aircraft-models', strict_slashes=False)
def index():
    models = AircraftModel.query() \
        .order_by(AircraftModel.kind) \
        .order_by(AircraftModel.name) \
        .all()

    return jsonify(models=AircraftModelSchema().dump(models, many=True).data)
