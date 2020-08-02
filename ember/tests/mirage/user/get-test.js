import { setupTest } from 'ember-qunit';
import { module, test } from 'qunit';

import setupMirage from 'ember-cli-mirage/test-support/setup-mirage';
import fetch from 'fetch';

module('Mirage | User', function (hooks) {
  setupTest(hooks);
  setupMirage(hooks);

  module('GET /api/users/:id', function () {
    test('returns the requested user', async function (assert) {
      let user = this.server.create('user');

      let response = await fetch(`/api/users/${user.id}`);
      assert.equal(response.status, 200);

      let responsePayload = await response.json();
      assert.matchJson(responsePayload, {
        id: 1,
        club: null,
        firstName: 'John',
        followers: 107,
        following: 128,
        lastName: 'Doe',
        name: 'John Doe',
        trackingCallsign: 'JD',
        trackingDelay: 0,
      });
    });

    test('returns the requested user and club', async function (assert) {
      let user = this.server.create('user');
      let club = this.server.create('club', { owner: user });
      user.update({ club });

      let response = await fetch(`/api/users/${user.id}`);
      assert.equal(response.status, 200);

      let responsePayload = await response.json();
      assert.matchJson(responsePayload, {
        id: 1,
        club: {
          id: 1,
          name: 'AeroClub Aachen',
        },
        firstName: 'John',
        followers: 107,
        following: 128,
        lastName: 'Doe',
        name: 'John Doe',
        trackingCallsign: 'JD',
        trackingDelay: 0,
      });
    });

    test('returns 404 if the user does not exist', async function (assert) {
      let response = await fetch(`/api/users/42`);
      assert.equal(response.status, 404);
    });
  });
});
