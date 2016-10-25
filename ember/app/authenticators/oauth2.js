import Ember from 'ember';
import OAuth2PasswordGrant from 'ember-simple-auth/authenticators/oauth2-password-grant';

export default OAuth2PasswordGrant.extend({
  ajax: Ember.inject.service(),

  clientId: 'skylines.aero',
  serverTokenEndpoint: '/api/oauth/token',
  serverTokenRevocationEndpoint: '/api/oauth/revoke',

  authenticate() {
    return this._super(...arguments)
      .then(data => this._addSettings(data));
  },

  restore() {
    return this._super(...arguments)
      .then(data => this._addSettings(data));
  },

  _addSettings(data) {
    let headers = {};
    if (data.access_token) {
      headers['Authorization'] = `Bearer ${data.access_token}`;
    }

    return this.get('ajax').request('/api/settings', { headers }).then(settings => {
      data.settings = settings;
      return data;
    });
  },
});
