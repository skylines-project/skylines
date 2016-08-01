import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';

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

  pending: false,
  error: null,

  showPilotNameInput: Ember.computed.equal('pilotId', null),
  showCopilotNameInput: Ember.computed.equal('copilotId', null),

  sendChangeRequest() {
    let id = this.get('flightId');
    let json = this.getProperties('pilotId', 'pilotName', 'copilotId', 'copilotName');

    this.set('pending', true);
    this.get('ajax').request(`/flights/${id}/`, { method: 'POST', json }).then(() => {
      window.location = `/flights/${id}/`;

    }).catch(error => {
      this.set('error', error);

    }).finally(() => {
      this.set('pending', false);
    });
  },

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.sendChangeRequest();
        }
      });
    },
  },
});
