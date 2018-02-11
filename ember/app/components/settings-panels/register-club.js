import { inject as service } from '@ember/service';
import Component from '@ember/component';
import { validator, buildValidations } from 'ember-cp-validations';
import { task } from 'ember-concurrency';

const Validations = buildValidations({
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
        this.get('saveTask').perform();
      }
    },
  },

  saveTask: task(function * () {
    let json = this.getProperties('name');

    try {
      let { id } = yield this.get('ajax').request('/api/clubs', { method: 'PUT', json });

      this.setProperties({
        messageKey: 'club-was-registered',
        error: null,
      });

      this.get('account').set('club', { id, name: json.name });

    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),
});
