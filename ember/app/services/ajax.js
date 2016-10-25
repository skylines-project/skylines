import Ember from 'ember';
import AjaxService from 'ember-ajax/services/ajax';

export default AjaxService.extend({
  session: Ember.inject.service(),

  headers: Ember.computed('session.data.authenticated.access_token', function() {
    let headers = {};
    let authToken = this.get('session.data.authenticated.access_token');
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    return headers;
  }),

  options(url, options = {}) {
    if (options.json) {
      options.contentType = 'application/json';
      options.data = JSON.stringify(options.json);
      delete options.json;
    }

    return this._super(url, options);
  },
});
