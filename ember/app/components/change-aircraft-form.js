import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
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

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),

  classNames: ['panel-body'],

  flightId: null,
  models: [],
  modelId: null,
  registration: null,
  competitionId: null,

  pending: false,
  error: null,

  sendChangeRequest() {
    let id = this.get('flightId');
    let json = this.getProperties('modelId', 'registration', 'competitionId');

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
