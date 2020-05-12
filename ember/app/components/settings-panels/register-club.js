import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
import { validator, buildValidations } from 'ember-cp-validations';

const Validations = buildValidations({
  email: {
    descriptionKey: 'email-address',
    validators: [
      validator('presence', true),
      validator('format', { type: 'email' }, { allowBlank: false})
    ],
    debounce: 500,
  },
  name: {
    descriptionKey: 'name',
    validators: [
      validator('presence', {
        presence: true,
        ignoreBlank: true,
      }),
      validator('unique-club-name', {
        messageKey: 'club-exists-already',
      }),
    ],
    debounce: 500,
  },
  website: {
    descriptionKey: 'website',
    validators: [validator('format', { allowBlank: true, type: 'url' })],
    debounce: 500,
  }
});

export default Component.extend(Validations, {
  ajax: service(),
  account: service(),

  classNames: ['panel', 'panel-default'],

  name: null,
  messageKey: null,
  error: null,

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.saveTask.perform();
      alert("Your group won't appear in the Groups list until someone in your group uploads a flight.");
      }
    },
  },

  saveTask: task(function*() {
    let json = this.getProperties('email','name', 'website');


    try {
      let { id } = yield this.ajax.request('/api/clubs', { method: 'PUT', json });
      this.setProperties({

        messageKey: 'club-was-registered',
        error: null,
      });

      this.account.set('club', { id, name: json.name });
    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }

  }).drop(),

});
