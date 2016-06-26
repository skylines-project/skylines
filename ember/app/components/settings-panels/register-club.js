import Ember from 'ember';
import { validator, buildValidations } from 'ember-cp-validations';

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
  pending: false,
  messageKey: null,
  error: null,

  sendChangeRequest() {
    let json = this.getProperties('name');

    this.set('pending', true);
    this.get('ajax').request('/settings/club', { method: 'PUT', json }).then(({id}) => {
      this.setProperties({
        messageKey: 'club-was-registered',
        error: null,
      });

      this.get('account').set('club', { id, name: json.name });

    }).catch(error => {
      this.setProperties({ messageKey: null, error });

    }).finally(() => {
      this.set('pending', false);
    });
  },

  actions: {
    submit() {
      this.validate().then(({ validations }) => {
        if (validations.get('isValid')) {
          this.sendChangeRequest();
        }
      });
    },
  },
});
