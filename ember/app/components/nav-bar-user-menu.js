import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  account: Ember.inject.service(),
  session: Ember.inject.service(),

  tagName: '',

  logoutTask: task(function * () {
    yield this.get('session').invalidate();
  }).drop(),
});
