import { getOwner } from '@ember/application';
import { oneWay } from '@ember/object/computed';
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

export default Component.extend(Validations, {
  ajax: service(),

  classNames: ['panel-body'],

  error: null,

  name: oneWay('club.name'),
  website: oneWay('club.website'),

  init() {
    this._super(...arguments);
    this.set('router', getOwner(this).lookup('router:main'));
  },

  actions: {
    async submit() {
      let { validations } = await this.validate();
      if (validations.get('isValid')) {
        this.get('saveTask').perform();
      }
    },
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
});
