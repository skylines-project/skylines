import Ember from 'ember';
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

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),

  classNames: ['panel-body'],

  pending: false,
  error: null,

  sendRequest() {
    let json = this.getProperties('email');

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
