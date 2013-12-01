# -*- coding: utf-8 -*-

from skylines.model import MountainWaveProject, Location
from skylines.lib.string import isnumeric


def get_waves_by_location(location):
    if not isinstance(location, Location):
        raise TypeError('Invalid `location` parameter.')

    waves = MountainWaveProject.by_location(location)
    return map(wave_to_dict, waves)


def wave_to_dict(wave):
    wind_direction = wave.main_wind_direction or ''
    if isnumeric(wind_direction):
        wind_direction += u'°'

    return {
        'name': wave.name,
        'main_wind_direction': wind_direction,
    }
