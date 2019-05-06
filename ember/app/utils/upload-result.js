import EmberObject from '@ember/object';
import { alias, equal } from '@ember/object/computed';

import { validator, buildValidations } from 'ember-cp-validations';

export const Validations = buildValidations({
  pilotName: {
    descriptionKey: 'pilot',
    validators: [validator('length', { max: 255 })],
    debounce: 500,
  },
  copilotId: {
    descriptionKey: 'copilot',
    validators: [validator('not-equal', { on: 'pilotId', messageKey: 'pilots-must-not-be-equal' })],
    debounce: 0,
  },
  copilotName: {
    descriptionKey: 'copilot',
    validators: [validator('length', { max: 255 })],
    debounce: 500,
  },
  registration: {
    descriptionKey: 'registration',
    validators: [validator('length', { max: 32 })],
    debounce: 500,
  },
  competitionId: {
    descriptionKey: 'competition-id',
    validators: [validator('length', { max: 5 })],
    debounce: 500,
  },
});

export default EmberObject.extend(Validations, {
  pilotId: alias('flight.pilotId'),
  pilotName: alias('flight.pilotName'),

  copilotId: alias('flight.copilotId'),
  copilotName: alias('flight.copilotName'),

  modelId: alias('flight.modelId'),
  registration: alias('flight.registration'),
  competitionId: alias('flight.competitionId'),

  success: equal('status', 0),
});
