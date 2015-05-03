from flask import Blueprint
from webargs import Arg
from webargs.flaskparser import use_args

from skylines.model import Bounds
from skylines import api
from .json import jsonify

airports_blueprint = Blueprint('airports', 'skylines')

bbox_args = {
    'bbox': Arg(Bounds.from_bbox_string, required=True, location='query',
                error='Invalid "bbox" parameter'),
}


@airports_blueprint.route('/')
@use_args(bbox_args)
def list(args):
    airports = api.get_airports_by_bbox(args['bbox'])
    return jsonify(airports)


@airports_blueprint.route('/<int:id>')
def details(id):
    airport = api.get_airport(id)
    return jsonify(airport)
