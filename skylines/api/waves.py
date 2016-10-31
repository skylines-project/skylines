from skylines.api.schemas import wave_list_schema
from skylines.model import MountainWaveProject


def get_waves_by_location(location):
    waves = MountainWaveProject.by_location(location)
    data, errors = wave_list_schema.dump(waves, many=True)
    return data
