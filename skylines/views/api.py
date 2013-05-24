# -*- coding: utf-8 -*-

from flask import Blueprint, request, abort, jsonify
from flask.ext.babel import _

from skylines.model import Airspace, MountainWaveProject, Location
from skylines.lib.string import isnumeric

api_blueprint = Blueprint('api', 'skylines')


def _query_airspace():
    try:
        latitude = float(request.args['lat'])
        longitude = float(request.args['lon'])

    except (KeyError, ValueError):
        abort(400)

    location = Location(latitude=latitude,
                        longitude=longitude)

    airspaces = Airspace.get_info(location)
    info = []

    for airspace in airspaces:
        info.append(dict(name=airspace.name,
                         base=airspace.base,
                         top=airspace.top,
                         airspace_class=airspace.airspace_class,
                         country=airspace.country_code))

    return info


def _query_waves():
    try:
        latitude = float(request.args['lat'])
        longitude = float(request.args['lon'])

    except (KeyError, ValueError):
        abort(400)

    location = Location(latitude=latitude,
                        longitude=longitude)

    mwp = MountainWaveProject.get_info(location)

    mwp_info = []
    for wave in mwp:
        if wave.main_wind_direction:
            if isnumeric(wave.main_wind_direction):
                wind_direction = wave.main_wind_direction + u"°"
            else:
                wind_direction = wave.main_wind_direction
        else:
            wind_direction = _("Unknown")

        mwp_info.append(dict(name=wave.name,
                             main_wind_direction=wind_direction
                             ))

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
