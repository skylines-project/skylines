from sprox.widgets import PropertySingleSelectField

from skylines.lib.formatter import units


class SelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        d['options'] = list(enumerate(x[0] for x in self.unit_registry))
        return d


class DistanceSelectField(SelectField):
    unit_registry = units.DISTANCE_UNITS


class SpeedSelectField(SelectField):
    unit_registry = units.SPEED_UNITS


class LiftSelectField(SelectField):
    unit_registry = units.LIFT_UNITS


class AltitudeSelectField(SelectField):
    unit_registry = units.ALTITUDE_UNITS


class PresetSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        d['options'] = list(enumerate(x[0] for x in units.UNIT_PRESETS))
        return d
