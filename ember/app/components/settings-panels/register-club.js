import Ember from 'ember';
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

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),
  account: Ember.inject.service(),

  classNames: ['panel', 'panel-default'],

  name: null,
  messageKey: null,
  error: null,

  saveTask: task(function * () {
    let json = this.getProperties('name');

    try {
      let { id } = yield this.get('ajax').request('/settings/club', { method: 'PUT', json });

      this.setProperties({
        messageKey: 'club-was-registered',
        error: null,
      });

      this.get('account').set('club', { id, name: json.name });

    } catch (error) {
      this.setProperties({ messageKey: null, error });
    }
  }).drop(),

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.get('saveTask').perform();
        }
      });
    },
  },
});
