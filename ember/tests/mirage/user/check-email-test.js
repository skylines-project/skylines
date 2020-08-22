import { module, test } from 'qunit';

import setupMirage from 'ember-cli-mirage/test-support/setup-mirage';
import fetch from 'fetch';

import { setupTest } from '../../test-helpers';

module('Mirage | User', function (hooks) {
  setupTest(hooks);
  setupMirage(hooks);

  module('POST /api/users/check-email', function () {
    test('returns `self` if the email matches the current user', async function (assert) {
      let user = this.server.create('user', { email: 'foo@bar.com' });
      this.server.create('mirage-session', { user });

      let response = await fetch('/api/users/check-email', {
        method: 'POST',
        body: JSON.stringify({ email: 'foo@bar.com' }),
      });
      assert.equal(response.status, 200);

      let responsePayload = await response.json();
      assert.matchJson(responsePayload, { result: 'self' });
    });

    test('returns `unavailable` if the email matches an existing user', async function (assert) {
      this.server.create('user', { email: 'foo@bar.com' });

      let response = await fetch('/api/users/check-email', {
        method: 'POST',
        body: JSON.stringify({ email: 'foo@bar.com' }),
      });
      assert.equal(response.status, 200);

      let responsePayload = await response.json();
      assert.matchJson(responsePayload, { result: 'unavailable' });
    });

    test('returns `available` if the email matches no existing user', async function (assert) {
      let response = await fetch('/api/users/check-email', {
        method: 'POST',
        body: JSON.stringify({ email: 'foo@bar.com' }),
      });
      assert.equal(response.status, 200);

      let responsePayload = await response.json();
      assert.matchJson(responsePayload, { result: 'available' });
    });
  });
});
