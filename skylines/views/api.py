# -*- coding: utf-8 -*-

from flask import Blueprint, request, abort, json, current_app
from werkzeug.exceptions import BadRequest

from skylines.model import (
    Airspace, MountainWaveProject, Location, Bounds
)
from skylines.lib.string import isnumeric
from skylines import api

api_blueprint = Blueprint('api', 'skylines')


@api_blueprint.errorhandler(TypeError)
@api_blueprint.errorhandler(ValueError)
def raise_bad_request(e):
    return jsonify({
        'message': e.message,
    }, status=400)


@api_blueprint.errorhandler(LookupError)
def raise_not_found(e):
    return jsonify({
        'message': e.message,
    }, status=404)


def jsonify(data, status=200):
    if not isinstance(data, (dict, list)):
        raise TypeError

    # Determine JSON indentation
    indent = None
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and not request.is_xhr:
        indent = 2

    # Determine if this is a JSONP request
    callback = request.args.get('callback', False)
    if callback:
        content = str(callback) + '(' + json.dumps({
            'meta': {
                'status': status,
            },
            'data': data,
        }, indent=indent) + ')'
        mimetype = 'application/javascript'
        status = 200

    else:
        content = json.dumps(data, indent=indent)
        mimetype = 'application/json'

    return current_app.response_class(
        content, mimetype=mimetype), status


def parse_location():
    try:
        latitude = float(request.args['lat'])
        longitude = float(request.args['lon'])
        return Location(latitude=latitude, longitude=longitude)

    except (KeyError, ValueError):
        abort(400)


def airspace_to_json(airspace):
    return {
        'name': airspace.name,
        'base': airspace.base,
        'top': airspace.top,
        'airspace_class': airspace.airspace_class,
        'country': airspace.country_code,
    }


def _query_airspace(location):
    airspaces = Airspace.by_location(location)
    return map(airspace_to_json, airspaces)


def wave_to_json(wave):
    wind_direction = wave.main_wind_direction or ''
    if isnumeric(wind_direction):
        wind_direction += u'°'

    return {
        'name': wave.name,
        'main_wind_direction': wind_direction,
    }


def _query_waves(location):
    waves = MountainWaveProject.by_location(location)
    return map(wave_to_json, waves)


@api_blueprint.route('/mapitems')
def mapitems():
    location = parse_location()
    return jsonify(dict(
        airspaces=_query_airspace(location),
        waves=_query_waves(location),
    ))


@api_blueprint.route('/airspace')
def airspace():
    location = parse_location()
    return jsonify(_query_airspace(location))


@api_blueprint.route('/mountain_wave_project')
def waves():
    location = parse_location()
    return jsonify(_query_waves(location))


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
