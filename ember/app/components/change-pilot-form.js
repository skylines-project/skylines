import Component from '@ember/component';
import { oneWay } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

import isNone from '../computed/is-none';

const Validations = buildValidations({
  pilotId: {
    descriptionKey: 'pilot',
    validators: [],
    debounce: 0,
  },
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
});

export default Component.extend(Validations, {
  tagName: '',
  ajax: service(),
  account: service(),

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
        this.saveTask.perform();
      }
    },
  },

  saveTask: task(function*() {
    let id = this.flightId;
    let json = this.getProperties('pilotId', 'pilotName', 'copilotId', 'copilotName');

    try {
      yield this.ajax.request(`/api/flights/${id}/`, { method: 'POST', json });
      this.onDidSave();
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
