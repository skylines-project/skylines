import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
  password: {
    descriptionKey: 'password',
    validators: [
      validator('presence', true),
      validator('current-password', {
        messageKey: 'wrong-current-password',
      }),
    ],
    debounce: 500,
  },
});

export default Component.extend(Validations, {
  tagName: '',
  ajax: service(),
  session: service(),

  password: null,

  messageKey: null,
  error: null,

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.deleteTask.perform();
      }
    },
  },

  deleteTask: task(function*() {
    let json = this.getProperties('password');

    try {
      yield this.ajax.request('/api/account', { method: 'DELETE', json });
      yield this.session.invalidate();
    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),
});
