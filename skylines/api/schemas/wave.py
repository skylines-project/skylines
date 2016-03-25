from marshmallow import fields

from skylines.api.schemas.base import BaseSchema
from skylines.lib.string import isnumeric


class WaveSchema(BaseSchema):
    name = fields.String()
    main_wind_direction = fields.Method('_wind_direction')

    @staticmethod
    def _wind_direction(wave):
        wind_direction = wave.main_wind_direction or ''
        if isnumeric(wind_direction):
            wind_direction += u'\u00B0'

        return wind_direction
