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
      validator('unique-email', { validResults: ['unavailable'], messageKey: 'email-unknown' }),
    ],
    debounce: 500,
  },
});

export default Component.extend(Validations, {
  ajax: service(),

  classNames: ['panel-body'],

  pending: false,
  error: null,

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.get('recoverTask').perform();
      }
    },
  },

  recoverTask: task(function * () {
    let json = this.getProperties('email');

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
