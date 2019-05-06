import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

export default Component.extend({
  ajax: service(),

  classNames: ['panel panel-default'],

  key: null,
  error: null,

  saveTask: task(function*() {
    try {
      let { key } = yield this.ajax.request('/api/settings/tracking/key', { method: 'POST' });
      this.setProperties({ key, error: null });
    } catch (error) {
      this.setProperties({ error });
    }
  }).drop(),
});
