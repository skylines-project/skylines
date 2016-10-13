import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';

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

  error: null,

  saveTask: task(function * () {
    let id = this.get('flightId');
    let json = this.getProperties('modelId', 'registration', 'competitionId');

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
