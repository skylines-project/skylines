from flask import Blueprint, request
from werkzeug.exceptions import BadRequest

from skylines.model import Bounds
from skylines import api
from .json import jsonify

airports_blueprint = Blueprint('airports', 'skylines')


@airports_blueprint.route('/')
def list():
    bbox = request.args.get('bbox', type=Bounds.from_bbox_string)
    if not bbox:
        raise BadRequest('Invalid `bbox` parameter.')

    airports = api.get_airports_by_bbox(bbox)
    return jsonify(airports)


@airports_blueprint.route('/<int:id>')
def details(id):
    airport = api.get_airport(id)
    return jsonify(airport)
