import Component from '@ember/component';
import { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

export default class TrackingKey extends Component {
  tagName = '';

  @service ajax;

  key = null;
  error = null;

  @(task(function* () {
    try {
      let { key } = yield this.ajax.request('/api/settings/tracking/key', { method: 'POST' });
      this.setProperties({ key, error: null });
    } catch (error) {
      this.setProperties({ error });
    }
  }).drop())
  saveTask;
}
