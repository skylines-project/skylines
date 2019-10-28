import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
  name: {
    descriptionKey: 'name',
    validators: [
      validator('presence', {
        presence: true,
        ignoreBlank: true,
      }),
      validator('unique-club-name', {
        messageKey: 'club-exists-already',
      }),
    ],
    debounce: 500,
  },
});

export default Component.extend(Validations, {
  tagName: '',
  ajax: service(),
  account: service(),

  name: null,
  messageKey: null,
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
    let json = this.getProperties('name');

    try {
      let { id } = yield this.ajax.request('/api/clubs', { method: 'PUT', json });

      this.setProperties({
        messageKey: 'club-was-registered',
        error: null,
      });

      this.account.set('club', { id, name: json.name });
    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),
});
