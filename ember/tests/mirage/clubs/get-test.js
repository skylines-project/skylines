import { setupTest } from 'ember-qunit';
import { module, test } from 'qunit';

import setupMirage from 'ember-cli-mirage/test-support/setup-mirage';
import fetch from 'fetch';

module('Mirage | Clubs', function (hooks) {
  setupTest(hooks);
  setupMirage(hooks);

  module('GET /api/clubs/:id', function () {
    test('returns the requested club', async function (assert) {
      let club = this.server.create('club');

      let response = await fetch(`/api/clubs/${club.id}`);
      assert.equal(response.status, 200);

      let responsePayload = await response.json();
      assert.matchJson(responsePayload, {
        id: 1,
        name: 'AeroClub Aachen',
        owner: null,
        timeCreated: '2020-05-24T21:41:03Z',
        website: 'https://acac.aero/',
      });
    });

    test('returns the requested club and owner', async function (assert) {
      let user = this.server.create('user');
      let club = this.server.create('club', { owner: user });

      let response = await fetch(`/api/clubs/${club.id}`);
      assert.equal(response.status, 200);

      let responsePayload = await response.json();
      assert.matchJson(responsePayload, {
        id: 1,
        name: 'AeroClub Aachen',
        owner: {
          id: 1,
          name: 'John Doe',
        },
        timeCreated: '2020-05-24T21:41:03Z',
        website: 'https://acac.aero/',
      });
    });

    test('returns 404 if the club does not exist', async function (assert) {
      let response = await fetch(`/api/clubs/42`);
      assert.equal(response.status, 404);
    });
  });
});
