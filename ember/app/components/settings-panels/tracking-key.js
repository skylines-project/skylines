import Ember from 'ember';
import { task } from 'ember-concurrency';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),

  classNames: ['panel panel-default'],

  key: null,
  error: null,

  saveTask: task(function * () {
    try {
      let { key } = yield this.get('ajax').request('/settings/tracking/key', { method: 'POST' });
      this.setProperties({ key, error: null });
    } catch (error) {
      this.setProperties({ error });
    }
  }).drop(),
});
