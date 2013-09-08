# -*- coding: utf-8 -*-

from flask import Blueprint, request, abort, jsonify
from werkzeug.exceptions import BadRequest

from skylines.model import (
    Airspace, Airport, MountainWaveProject, Location, Bounds
)
from skylines.lib.decorators import jsonp
from skylines.lib.string import isnumeric

api_blueprint = Blueprint('api', 'skylines')


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
@jsonp
def mapitems():
    location = parse_location()
    return jsonify(airspaces=_query_airspace(location),
                   waves=_query_waves(location))


@api_blueprint.route('/airspace')
@jsonp
def airspace():
    location = parse_location()
    return jsonify(airspaces=_query_airspace(location))


@api_blueprint.route('/mountain_wave_project')
@jsonp
def waves():
    location = parse_location()
    return jsonify(waves=_query_waves(location))


@api_blueprint.route('/airports/')
@jsonp
def airports():
    bbox = request.args.get('bbox', type=Bounds.from_bbox_string)
    if not bbox:
        raise BadRequest('Invalid `bbox` parameter.')

    bbox.normalize()
    if bbox.get_size() > 20 * 20:
        raise BadRequest('Requested `bbox` is too large.')

    airports = map(airport_to_json, Airport.by_bbox(bbox))
    return jsonify(airports=airports)


@api_blueprint.route('/airports/<int:id>')
@jsonp
def airport(id):
    airport = Airport.get(id)
    if not airport:
        abort(404)

    airport = airport_to_json(airport, short=False)
    return jsonify(airport)


def airport_to_json(airport, short=True):
    json = {
        'id': airport.id,
        'name': airport.name,
        'elevation': airport.altitude,
        'location': {
            'latitude': airport.location.latitude,
            'longitude': airport.location.longitude,
        },
    }

    if not short:
        json.update({
            'icao': airport.icao,
            'short_name': airport.short_name,
            'country_code': airport.country_code,
            'type': airport.type,
            'runways': [{
                'length': airport.runway_len,
                'direction': airport.runway_dir,
                'surface': airport.surface,
            }],
            'frequencies': [{
                'frequency': airport.frequency,
            }],
        })

    return json
