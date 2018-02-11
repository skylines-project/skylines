import { inject as service } from '@ember/service';
import Component from '@ember/component';
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

export default Component.extend(Validations, {
  ajax: service(),

  classNames: ['panel-body'],

  flightId: null,
  models: null,
  modelId: null,
  registration: null,
  competitionId: null,
  onDidSave() {},

  error: null,

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
    let json = this.getProperties('modelId', 'registration', 'competitionId');

    try {
      yield this.get('ajax').request(`/api/flights/${id}/`, { method: 'POST', json });
      this.get('onDidSave')();
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
