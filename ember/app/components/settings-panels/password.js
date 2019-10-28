import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
  currentPassword: {
    descriptionKey: 'current-password',
    validators: [
      validator('presence', true),
      validator('current-password', {
        messageKey: 'wrong-current-password',
      }),
    ],
    debounce: 500,
  },
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

  currentPassword: null,
  password: null,
  passwordConfirmation: null,
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
    let json = this.getProperties('currentPassword', 'password');

    try {
      yield this.ajax.request('/api/settings/', { method: 'POST', json });
      this.setProperties({
        messageKey: 'password-was-changed',
        error: null,
      });
    } catch (error) {
      this.setProperties({
        messageKey: null,
        error,
      });
    }
  }).drop(),
});
