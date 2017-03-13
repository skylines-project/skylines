import Ember from 'ember';
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

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),

  classNames: ['panel-body'],

  pending: false,
  error: null,

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.get('recoverTask').perform();
        }
      });
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
