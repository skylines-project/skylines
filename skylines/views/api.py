# -*- coding: utf-8 -*-

from flask import Blueprint, request, abort, jsonify
from flask.ext.babel import _

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


def _query_airspace():
    location = parse_location()

    airspaces = Airspace.get_info(location)
    info = []

    for airspace in airspaces:
        info.append(dict(name=airspace.name,
                         base=airspace.base,
                         top=airspace.top,
                         airspace_class=airspace.airspace_class,
                         country=airspace.country_code))

    return info


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

    waves = MountainWaveProject.get_info(location)

    mwp_info = []
    for wave in waves:
        mwp_info.append(wave_to_json(wave))

    return mwp_info


@api_blueprint.route('/')
def index():
    return jsonify(airspaces=_query_airspace(), waves=_query_waves())


@api_blueprint.route('/airspace')
def airspace():
    return jsonify(airspaces=_query_airspace())


@api_blueprint.route('/mountain_wave_project')
def waves():
    return jsonify(waves=_query_waves())
