import { inject as service } from '@ember/service';

import OAuth2PasswordGrant from 'ember-simple-auth/authenticators/oauth2-password-grant';

export default OAuth2PasswordGrant.extend({
  ajax: service(),

  clientId: 'skylines.aero',
  serverTokenEndpoint: '/api/oauth/token',
  serverTokenRevocationEndpoint: '/api/oauth/revoke',

  async authenticate() {
    let data = await this._super(...arguments);
    return this._addSettings(data);
  },

  async restore() {
    let data = await this._super(...arguments);
    return this._addSettings(data);
  },

  async _addSettings(data) {
    let headers = {};
    if (data.access_token) {
      headers['Authorization'] = `Bearer ${data.access_token}`;
    }

    data.settings = await this.ajax.request('/api/settings', { headers });
    return data;
  },
});
