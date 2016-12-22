from .airspace import AirspaceSchema
from .wave import WaveSchema

__all__ = [
    AirspaceSchema,
    WaveSchema,
]

airspace_list_schema = AirspaceSchema(only=('name', '_class', 'top', 'base', 'country'))
wave_list_schema = WaveSchema()
