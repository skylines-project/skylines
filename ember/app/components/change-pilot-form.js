import Ember from 'ember';
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

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),
  account: Ember.inject.service(),

  classNames: ['panel-body'],

  flightId: null,
  flight: null,
  clubMembers: [],

  pilotId: Ember.computed.oneWay('flight.pilot.id'),
  pilotName: Ember.computed.oneWay('flight.pilotName'),
  copilotId: Ember.computed.oneWay('flight.copilot.id'),
  copilotName: Ember.computed.oneWay('flight.copilotName'),

  error: null,

  showPilotNameInput: isNone('pilotId'),
  showCopilotNameInput: isNone('copilotId'),

  saveTask: task(function * () {
    let id = this.get('flightId');
    let json = this.getProperties('pilotId', 'pilotName', 'copilotId', 'copilotName');

    try {
      yield this.get('ajax').request(`/flights/${id}/`, { method: 'POST', json });
      window.location = `/flights/${id}/`;
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.get('saveTask').perform();
        }
      });
    },
  },
});
