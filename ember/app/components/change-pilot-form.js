import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
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

  pilotId: Ember.computed.oneWay('flight.pilotId'),
  pilotName: Ember.computed.oneWay('flight.pilotName'),
  copilotId: Ember.computed.oneWay('flight.copilotId'),
  copilotName: Ember.computed.oneWay('flight.copilotName'),

  pending: false,
  error: null,

  pilots: Ember.computed('account.user', 'account.club', 'clubMembers.[]', function() {
    let pilots = [{ id: null }, this.get('account.user')];
    if (this.get('account.club')) {
      pilots.push({ groupName: this.get('account.club.name'), options: this.get('clubMembers') });
    }
    return pilots;
  }),

  pilot: Ember.computed('pilotId', {
    get() {
      return this.findPilot(this.get('pilotId'));
    },
    set(key, value) {
      this.set('pilotId', value.id);
      return value;
    },
  }),

  showPilotNameInput: Ember.computed.equal('pilotId', null),

  copilot: Ember.computed('copilotId', {
    get() {
      return this.findPilot(this.get('copilotId'));
    },
    set(key, value) {
      this.set('copilotId', value.id);
      return value;
    },
  }),

  showCopilotNameInput: Ember.computed.equal('copilotId', null),

  findPilot(id) {
    let pilots = this.get('pilots');
    return pilots.findBy('id', id) || pilots.get('lastObject.options').findBy('id', id);
  },

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
