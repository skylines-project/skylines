import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';

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

  recoverTask: task(function * () {
    let json = this.getProperties('password', 'recoveryKey');

    try {
      yield this.get('ajax').request('/users/recover', { method: 'POST', json });
      this.set('error', null);
      this.set('success', true);
    } catch (error) {
      this.set('error', error);
      this.set('success', false);
    }
  }).drop(),

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.get('recoverTask').perform();
        }
      });
    },
  },
});
