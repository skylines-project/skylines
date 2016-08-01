import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';

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

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),

  classNames: ['panel-body'],

  pending: false,
  error: null,

  sendRequest() {
    let json = this.getProperties('email', 'firstName', 'lastName', 'password');

    this.set('pending', true);
    this.get('ajax').request('/users/new', { method: 'POST', json }).then(() => {
      window.location = '/login';

    }).catch(error => {
      this.set('error', error);

    }).finally(() => {
      this.set('pending', false);
    });
  },

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.sendRequest();
        }
      });
    },
  },
});
