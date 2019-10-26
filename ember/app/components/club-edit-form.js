import { getOwner } from '@ember/application';
import Component from '@ember/component';
import { oneWay } from '@ember/object/computed';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';
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
    validators: [validator('format', { allowBlank: true, type: 'url' })],
    debounce: 500,
  },
});

export default Component.extend(Validations, {
  tagName: '',

  ajax: service(),

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
        this.saveTask.perform();
      }
    },
  },

  saveTask: task(function*() {
    let id = this.get('club.id');
    let json = this.getProperties('name', 'website');

    try {
      yield this.ajax.request(`/api/clubs/${id}`, { method: 'POST', json });
      this.set('club.name', json.name);
      this.set('club.website', json.website);
      this.router.transitionTo('club', id);
    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
