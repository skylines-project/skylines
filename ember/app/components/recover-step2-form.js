import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
  password: {
    descriptionKey: 'password',
    validators: [validator('presence', true), validator('length', { min: 6 })],
    debounce: 500,
  },
  passwordConfirmation: validator('confirmation', {
    on: 'password',
    messageKey: 'passwords-do-not-match',
  }),
});

export default Component.extend(Validations, {
  tagName: '',

  ajax: service(),

  recoveryKey: null,

  pending: false,
  error: null,
  success: false,

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.recoverTask.perform();
      }
    },
  },

  recoverTask: task(function*() {
    let json = this.getProperties('password', 'recoveryKey');

    try {
      yield this.ajax.request('/api/users/recover', { method: 'POST', json });
      this.set('error', null);
      this.set('success', true);
    } catch (error) {
      this.set('error', error);
      this.set('success', false);
    }
  }).drop(),
});
