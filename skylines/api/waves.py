from skylines.api.schemas import wave_list_schema
from skylines.model import MountainWaveProject, Location


def get_waves_by_location(location):
    if not isinstance(location, Location):
        raise TypeError('Invalid `location` parameter.')

    waves = MountainWaveProject.by_location(location)
    data, errors = wave_list_schema.dump(waves, many=True)
    return data
