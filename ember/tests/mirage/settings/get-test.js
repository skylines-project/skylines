import { setupTest } from 'ember-qunit';
import { module, test } from 'qunit';

import setupMirage from 'ember-cli-mirage/test-support/setup-mirage';
import fetch from 'fetch';

module('Mirage | Settings', function (hooks) {
  setupTest(hooks);
  setupMirage(hooks);

  module('GET /api/settings', function () {
    test('returns the current user', async function (assert) {
      let user = this.server.create('user');
      this.server.create('mirage-session', { user });

      let response = await fetch('/api/settings');
      assert.equal(response.status, 200);

      let responsePayload = await response.json();
      assert.matchJson(responsePayload, {
        id: 1,
        altitudeUnit: 0,
        club: null,
        distanceUnit: 1,
        email: 'johnny.dee@gmail.com',
        firstName: 'John',
        followers: 107,
        following: 128,
        lastName: 'Doe',
        liftUnit: 0,
        name: 'John Doe',
        speedUnit: 1,
        trackingCallsign: 'JD',
        trackingDelay: 0,
        trackingKey: 'ABCDEF42',
      });
    });

    test('returns 401 if no session exists', async function (assert) {
      let response = await fetch('/api/settings');
      assert.equal(response.status, 401);
    });
  });
});
