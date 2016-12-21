import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';

export const Validations = buildValidations({
  pilotName: {
    descriptionKey: 'pilot',
    validators: [
      validator('length', { max: 255 }),
    ],
    debounce: 500,
  },
  copilotId: {
    descriptionKey: 'copilot',
    validators: [
      validator('not-equal', { on: 'pilotId', messageKey: 'pilots-must-not-be-equal' }),
    ],
    debounce: 0,
  },
  copilotName: {
    descriptionKey: 'copilot',
    validators: [
      validator('length', { max: 255 }),
    ],
    debounce: 500,
  },
  registration: {
    descriptionKey: 'registration',
    validators: [
      validator('length', { max: 32 }),
    ],
    debounce: 500,
  },
  competitionId: {
    descriptionKey: 'competition-id',
    validators: [
      validator('length', { max: 5 }),
    ],
    debounce: 500,
  },
});

export default Ember.Object.extend(Validations, {
  pilotId: Ember.computed.alias('flight.pilotId'),
  pilotName: Ember.computed.alias('flight.pilotName'),

  copilotId: Ember.computed.alias('flight.copilotId'),
  copilotName: Ember.computed.alias('flight.copilotName'),

  modelId: Ember.computed.alias('flight.modelId'),
  registration: Ember.computed.alias('flight.registration'),
  competitionId: Ember.computed.alias('flight.competitionId'),

  success: Ember.computed.equal('status', 0),
});
