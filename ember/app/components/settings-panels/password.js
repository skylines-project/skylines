import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';

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
    validators: [
      validator('presence', true),
      validator('length', { min: 6 }),
    ],
    debounce: 500,
  },
  passwordConfirmation: validator('confirmation', {
    on: 'password',
    messageKey: 'passwords-do-not-match',
  }),
});

export default Component.extend(Validations, {
  ajax: service(),

  classNames: ['panel', 'panel-default'],

  currentPassword: null,
  password: null,
  passwordConfirmation: null,
  messageKey: null,
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
    let json = this.getProperties('currentPassword', 'password');

    try {
      yield this.get('ajax').request('/api/settings/', { method: 'POST', json });
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
