import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
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

  recoveryKey: null,

  pending: false,
  error: null,
  success: false,

  sendRequest() {
    let json = this.getProperties('password', 'recoveryKey');

    this.set('pending', true);
    this.get('ajax').request('/users/recover', { method: 'POST', json }).then(() => {
      this.set('error', null);
      this.set('success', true);

    }).catch(error => {
      this.set('error', error);
      this.set('success', false);

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
