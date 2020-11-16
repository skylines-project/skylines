import { computed, getProperties } from '@ember/object';
import { alias } from '@ember/object/computed';
import Service, { inject as service } from '@ember/service';

import { task } from 'ember-concurrency';

export default class AccountService extends Service {
  @service ajax;
  @service session;

  @alias('loadSettingsTask.lastSuccessful.value') sessionData;

  @computed('sessionData.{id,name}')
  get user() {
    let sessionData = this.sessionData;
    if (sessionData) {
      return getProperties(sessionData, 'id', 'name');
    }
  }

  @alias('sessionData.club') club;

  // eslint-disable-next-line require-await
  async loadSettings(accessToken) {
    return this.loadSettingsTask.perform(accessToken);
  }

  @(task(function* (accessToken) {
    let headers = {};
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    return yield this.ajax.request('/api/settings', { headers });
  }).restartable())
  loadSettingsTask;
}
