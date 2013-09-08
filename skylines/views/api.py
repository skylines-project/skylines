# -*- coding: utf-8 -*-

from flask import Blueprint, request, abort, jsonify

from skylines.model import Airspace, MountainWaveProject, Location
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


def _query_airspace():
    location = parse_location()
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


def _query_waves():
    location = parse_location()
    waves = MountainWaveProject.by_location(location)
    return map(wave_to_json, waves)


@api_blueprint.route('/')
def index():
    return jsonify(airspaces=_query_airspace(), waves=_query_waves())


@api_blueprint.route('/airspace')
def airspace():
    return jsonify(airspaces=_query_airspace())


@api_blueprint.route('/mountain_wave_project')
def waves():
    return jsonify(waves=_query_waves())
