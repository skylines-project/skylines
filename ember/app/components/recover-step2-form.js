import { inject as service } from '@ember/service';
import Component from '@ember/component';
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

export default Component.extend(Validations, {
  ajax: service(),

  classNames: ['panel-body'],

  recoveryKey: null,

  pending: false,
  error: null,
  success: false,

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.get('recoverTask').perform();
      }
    },
  },

  recoverTask: task(function * () {
    let json = this.getProperties('password', 'recoveryKey');

    try {
      yield this.get('ajax').request('/api/users/recover', { method: 'POST', json });
      this.set('error', null);
      this.set('success', true);
    } catch (error) {
      this.set('error', error);
      this.set('success', false);
    }
  }).drop(),
});
