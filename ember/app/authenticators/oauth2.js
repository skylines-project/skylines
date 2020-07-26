import { inject as service } from '@ember/service';

import OAuth2PasswordGrant from 'ember-simple-auth/authenticators/oauth2-password-grant';

export default class extends OAuth2PasswordGrant {
  @service account;

  clientId = 'skylines.aero';
  serverTokenEndpoint = '/api/oauth/token';
  serverTokenRevocationEndpoint = '/api/oauth/revoke';

  async authenticate() {
    let data = await super.authenticate(...arguments);
    return this._addSettings(data);
  }

  async restore() {
    let data = await super.restore(...arguments);
    return this._addSettings(data);
  }

  async _addSettings(data) {
    await this.account.loadSettings(data.access_token);
    return data;
  }
}
