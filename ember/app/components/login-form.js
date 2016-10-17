import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),

  classNameBindings: ['inline::panel-body'],

  inline: false,
  error: null,

  loginTask: task(function * () {
    let json = this.getProperties('email', 'password');

    try {
      yield this.get('ajax').request('/session', { method: 'PUT', json });

      let next = this.get('inline') ? window.location.href : this.get('next');
      window.location = next || '/';

    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
