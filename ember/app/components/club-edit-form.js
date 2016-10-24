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
  error: null,

  init() {
    this._super(...arguments);
    this.set('router', Ember.getOwner(this).lookup('router:main'));
  },

  saveTask: task(function * () {
    let id = this.get('club.id');
    let json = this.getProperties('name', 'website');

    try {
      yield this.get('ajax').request(`/api/clubs/${id}`, { method: 'POST', json });
      this.set('club.name', json.name);
      this.set('club.website', json.website);
      this.get('router').transitionTo('club', id);

    } catch (error) {
      this.set('error', error);
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
