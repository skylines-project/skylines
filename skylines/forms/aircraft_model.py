from flask.ext.babel import _

from tw.forms.fields import SingleSelectField

from skylines.forms.select import SelectField as _SelectField
from skylines.model import AircraftModel


class SelectField(SingleSelectField):
    def update_params(self, d):
        models = AircraftModel.query() \
            .order_by(AircraftModel.kind) \
            .order_by(AircraftModel.name) \
            .all()

        gliders = [(model.id, model) for model in models if model.kind == 1]
        motor_gliders = [(model.id, model) for model in models if model.kind == 2]
        hanggliders = [(model.id, model) for model in models if model.kind == 3]
        paragliders = [(model.id, model) for model in models if model.kind == 4]
        ul_gliders = [(model.id, model) for model in models if model.kind == 5]

        options = []

        if len(gliders) > 0: options.append((_('Gliders'), gliders))
        if len(motor_gliders) > 0: options.append((_('Motor Gliders'), motor_gliders))
        if len(hanggliders) > 0: options.append((_('Hanggliders'), hanggliders))
        if len(paragliders) > 0: options.append((_('Paragliders'), paragliders))
        if len(ul_gliders) > 0: options.append((_('UL Gliders'), ul_gliders))

        options.append((_('Other'), [(None, '[unspecified]')]))

        d['options'] = options
        return SingleSelectField.update_params(self, d)


class AircraftModelSelectField(_SelectField):
    def __init__(self, *args, **kwargs):
        super(AircraftModelSelectField, self).__init__(*args, **kwargs)
        self.coerce = int

        if not kwargs.get('_form'):
            self.process(None)

    def process(self, *args, **kwargs):
        models = AircraftModel.query() \
            .order_by(AircraftModel.kind) \
            .order_by(AircraftModel.name) \
            .all()

        gliders = [(model.id, model) for model in models if model.kind == 1]
        motor_gliders = [(model.id, model) for model in models if model.kind == 2]
        hanggliders = [(model.id, model) for model in models if model.kind == 3]
        paragliders = [(model.id, model) for model in models if model.kind == 4]
        ul_gliders = [(model.id, model) for model in models if model.kind == 5]

        self.choices = []

        if len(gliders) > 0: self.choices.append((_('Gliders'), gliders))
        if len(motor_gliders) > 0: self.choices.append((_('Motor Gliders'), motor_gliders))
        if len(hanggliders) > 0: self.choices.append((_('Hanggliders'), hanggliders))
        if len(paragliders) > 0: self.choices.append((_('Paragliders'), paragliders))
        if len(ul_gliders) > 0: self.choices.append((_('UL Gliders'), ul_gliders))

        self.choices.append((_('Other'), [(0, '[unspecified]')]))

        super(AircraftModelSelectField, self).process(*args, **kwargs)
