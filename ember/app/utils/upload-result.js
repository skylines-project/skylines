import EmberObject from '@ember/object';
import { equal, alias } from '@ember/object/computed';

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

export default class UploadResult extends EmberObject.extend(Validations) {
  @alias('flight.pilotId') pilotId;
  @alias('flight.pilotName') pilotName;
  @alias('flight.copilotId') copilotId;
  @alias('flight.copilotName') copilotName;
  @alias('flight.modelId') modelId;
  @alias('flight.registration') registration;
  @alias('flight.competitionId') competitionId;
  @equal('status', 0) success;
}
