import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
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

export default Component.extend(Validations, {
  tagName: '',

  ajax: service(),

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
        this.saveTask.perform();
      }
    },
  },

  saveTask: task(function*() {
    let id = this.flightId;
    let json = this.getProperties('modelId', 'registration', 'competitionId');

    try {
      yield this.ajax.request(`/api/flights/${id}/`, { method: 'POST', json });
      this.onDidSave();
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
