from tg.i18n import ugettext as _

from tw.forms.fields import SingleSelectField

from skylines.model import DBSession, AircraftModel


class SelectField(SingleSelectField):
    def update_params(self, d):
        models = DBSession.query(AircraftModel) \
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
