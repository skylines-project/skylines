from wtforms import SelectField

from skylines.lib.formatter import units


class UnitSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(SelectField, self).__init__(*args, **kwargs)
        self.coerce = int
        self.choices = list(enumerate(x[0] for x in self.unit_registry))


class DistanceUnitSelectField(UnitSelectField):
    unit_registry = units.DISTANCE_UNITS


class SpeedUnitSelectField(UnitSelectField):
    unit_registry = units.SPEED_UNITS


class LiftUnitSelectField(UnitSelectField):
    unit_registry = units.LIFT_UNITS


class AltitudeUnitSelectField(UnitSelectField):
    unit_registry = units.ALTITUDE_UNITS


class UnitsPresetSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(UnitsPresetSelectField, self).__init__(*args, **kwargs)
        self.coerce = int
        self.choices = list(enumerate(x[0] for x in units.UNIT_PRESETS))
