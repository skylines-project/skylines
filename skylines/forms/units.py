from sprox.widgets import PropertySingleSelectField

from skylines.lib.formatter import units


class SelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        d['options'] = list(enumerate(x[0] for x in self.unit_registry))
        return d


class DistanceSelectField(SelectField):
    unit_registry = units.distance_units


class SpeedSelectField(SelectField):
    unit_registry = units.speed_units


class LiftSelectField(SelectField):
    unit_registry = units.lift_units


class AltitudeSelectField(SelectField):
    unit_registry = units.altitude_units


class PresetSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        d['options'] = list(enumerate(x[0] for x in units.unit_presets))
        return d
