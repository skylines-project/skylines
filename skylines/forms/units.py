from sprox.widgets import PropertySingleSelectField

from skylines.lib.formatter import units


class UnitSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        d['options'] = list(enumerate(x[0] for x in self.unit_registry))
        return d


class DistanceUnitSelectField(UnitSelectField):
    unit_registry = units.distance_units


class SpeedUnitSelectField(UnitSelectField):
    unit_registry = units.speed_units


class LiftUnitSelectField(UnitSelectField):
    unit_registry = units.lift_units


class AltitudeUnitSelectField(UnitSelectField):
    unit_registry = units.altitude_units


class UnitPresetSelectField(PropertySingleSelectField):
    def _my_update_params(self, d, nullable=False):
        d['options'] = list(enumerate(x[0] for x in units.unit_presets))
        return d
