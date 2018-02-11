import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';

const Validations = buildValidations({
  email: {
    descriptionKey: 'email-address',
    validators: [
      validator('presence', true),
      validator('format', { type: 'email' }),
      validator('unique-email', { validResults: ['available'], messageKey: 'email-exists-already' }),
    ],
    debounce: 500,
  },
  firstName: {
    descriptionKey: 'first-name',
    validators: [
      validator('presence', true),
    ],
    debounce: 500,
  },
  lastName: {
    descriptionKey: 'last-name',
    validators: [
      validator('presence', true),
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

  classNames: ['panel-body'],

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
    let json = this.getProperties('email', 'firstName', 'lastName', 'password');

    try {
      yield this.get('ajax').request('/api/users', { method: 'POST', json });
      this.getWithDefault('transitionTo')('login');

    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
