import { computed } from '@ember/object';
import { inject as service } from '@ember/service';

import AjaxService from 'ember-ajax/services/ajax';

export default class extends AjaxService {
  @service session;

  @computed('session.data.authenticated.access_token')
  get headers() {
    let headers = {};
    let authToken = this.get('session.data.authenticated.access_token');
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    return headers;
  }

  options(url, options = {}) {
    if (options.json) {
      options.contentType = 'application/json';
      options.data = JSON.stringify(options.json);
      delete options.json;
    }

    return super.options(url, options);
  }
}
