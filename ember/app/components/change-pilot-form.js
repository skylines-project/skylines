import { oneWay } from '@ember/object/computed';
import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';

import isNone from '../computed/is-none';

const Validations = buildValidations({
  pilotId: {
    descriptionKey: 'pilot',
    validators: [],
    debounce: 0,
  },
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
});

export default Component.extend(Validations, {
  ajax: service(),
  account: service(),

  classNames: ['panel-body'],

  flightId: null,
  flight: null,
  clubMembers: null,
  onDidSave() {},

  error: null,

  pilotId: oneWay('flight.pilot.id'),
  pilotName: oneWay('flight.pilotName'),
  copilotId: oneWay('flight.copilot.id'),
  copilotName: oneWay('flight.copilotName'),

  showPilotNameInput: isNone('pilotId'),
  showCopilotNameInput: isNone('copilotId'),

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.get('saveTask').perform();
      }
    },
  },

  saveTask: task(function * () {
    let id = this.get('flightId');
    let json = this.getProperties('pilotId', 'pilotName', 'copilotId', 'copilotName');

    try {
      yield this.get('ajax').request(`/api/flights/${id}/`, { method: 'POST', json });
      this.get('onDidSave')();
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
