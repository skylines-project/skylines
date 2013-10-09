from wtforms import SelectField as _SelectField

from skylines.lib.formatter import units


class SelectField(_SelectField):
    def __init__(self, *args, **kwargs):
        super(SelectField, self).__init__(*args, **kwargs)
        self.coerce = int
        self.choices = list(enumerate(x[0] for x in self.unit_registry))


class DistanceSelectField(SelectField):
    unit_registry = units.DISTANCE_UNITS


class SpeedSelectField(SelectField):
    unit_registry = units.SPEED_UNITS


class LiftSelectField(SelectField):
    unit_registry = units.LIFT_UNITS


class AltitudeSelectField(SelectField):
    unit_registry = units.ALTITUDE_UNITS


class PresetSelectField(_SelectField):
    def __init__(self, *args, **kwargs):
        super(PresetSelectField, self).__init__(*args, **kwargs)
        self.coerce = int
        self.choices = list(enumerate(x[0] for x in units.UNIT_PRESETS))
