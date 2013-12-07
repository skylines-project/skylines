from flask import Blueprint, request, abort
from werkzeug.exceptions import BadRequest

from skylines.model import Location, Bounds
from skylines import api
from .json import jsonify
from .parser import parse_location

api_blueprint = Blueprint('api', 'skylines')


@api_blueprint.route('/mapitems')
def mapitems():
    location = parse_location(request.args)
    return jsonify({
        'airspaces': api.get_airspaces_by_location(location),
        'waves': api.get_waves_by_location(location),
    })


@api_blueprint.route('/airspace')
def airspace():
    location = parse_location(request.args)
    return jsonify(api.get_airspaces_by_location(location))


@api_blueprint.route('/mountain_wave_project')
def waves():
    location = parse_location(request.args)
    return jsonify(api.get_waves_by_location(location))


@api_blueprint.route('/airports/')
def airports():
    bbox = request.args.get('bbox', type=Bounds.from_bbox_string)
    if not bbox:
        raise BadRequest('Invalid `bbox` parameter.')

    airports = api.get_airports_by_bbox(bbox)
    return jsonify(airports)


@api_blueprint.route('/airports/<int:id>')
def airport(id):
    airport = api.get_airport(id)
    return jsonify(airport)
