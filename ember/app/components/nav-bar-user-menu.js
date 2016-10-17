import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  account: Ember.inject.service(),
  ajax: Ember.inject.service(),

  tagName: '',

  logoutTask: task(function * () {
    yield this.get('ajax').request('session', { method: 'DELETE' });
    document.location.reload();
  }).drop(),
});
