import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
  email: {
    descriptionKey: 'email-address',
    validators: [
      validator('presence', true),
      validator('format', { type: 'email' }),
      validator('unique-email', { validResults: ['unavailable'], messageKey: 'email-unknown' }),
    ],
    debounce: 500,
  },
});

export default Component.extend(Validations, {
  tagName: '',

  ajax: service(),

  pending: false,
  error: null,

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.recoverTask.perform();
      }
    },
  },

  recoverTask: task(function*() {
    let json = this.getProperties('email');

    try {
      let { url } = yield this.ajax.request('/api/users/recover', { method: 'POST', json });
      this.set('error', null);
      this.set('success', true);
      this.set('url', url);
    } catch (error) {
      this.set('error', error);
      this.set('success', false);
    }
  }).drop(),
});
