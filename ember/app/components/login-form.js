import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),

  classNames: ['panel-body'],

  error: null,

  loginTask: task(function * () {
    let json = this.getProperties('email', 'password');

    try {
      yield this.get('ajax').request('/session', { method: 'PUT', json });
      window.location = this.get('next') || '/';

    } catch (error) {
      this.set('error', error);
    }
  }).drop(),
});
