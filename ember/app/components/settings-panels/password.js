import Ember from 'ember';
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

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),

  classNames: ['panel', 'panel-default'],

  currentPassword: null,
  password: null,
  passwordConfirmation: null,
  messageKey: null,
  error: null,

  saveTask: task(function * () {
    let json = this.getProperties('currentPassword', 'password');

    try {
      yield this.get('ajax').request('/settings/', { method: 'POST', json });
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
