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
        idKey: 'club.id',
      }),
    ],
    debounce: 500,
  },
  website: {
    descriptionKey: 'website',
    validators: [
      validator('format', { allowBlank: true, type: 'url' }),
    ],
    debounce: 500,
  },
});

export default Ember.Component.extend(Validations, {
  ajax: Ember.inject.service(),

  classNames: ['panel-body'],

  name: Ember.computed.oneWay('club.name'),
  website: Ember.computed.oneWay('club.website'),
  pending: false,
  error: null,

  init() {
    this._super(...arguments);
    this.set('router', Ember.getOwner(this).lookup('router:main'));
  },

  sendChangeRequest() {
    let id = this.get('club.id');
    let json = this.getProperties('name', 'website');

    this.set('pending', true);
    this.get('ajax').request(`/clubs/${id}/`, { method: 'POST', json }).then(() => {
      this.set('club.name', json.name);
      this.set('club.website', json.website);
      this.get('router').transitionTo('club', id);

    }).catch(error => {
      this.set('error', error);

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
