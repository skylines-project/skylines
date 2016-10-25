from flask import Blueprint
from webargs.flaskparser import use_args

from skylines import api
from skylines.api.schemas.fields.bounds import BoundsField
from .json import jsonify

airports_blueprint = Blueprint('airports', 'skylines')

bbox_args = {
    'bbox': BoundsField(required=True, location='query'),
}


@airports_blueprint.route('/airports', strict_slashes=False)
@use_args(bbox_args)
def list(args):
    airports = api.get_airports_by_bbox(args['bbox'])
    return jsonify(airports)


@airports_blueprint.route('/airports/<int:id>')
def details(id):
    airport = api.get_airport(id)
    return jsonify(airport)
