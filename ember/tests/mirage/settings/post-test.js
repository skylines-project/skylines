import { module, test } from 'qunit';

import setupMirage from 'ember-cli-mirage/test-support/setup-mirage';
import fetch from 'fetch';

import { setupTest } from '../../test-helpers';

module('Mirage | Settings', function (hooks) {
  setupTest(hooks);
  setupMirage(hooks);

  module('POST /api/settings', function () {
    test('returns 401 if no session exists', async function (assert) {
      let response = await fetch('/api/settings', {
        method: 'POST',
        body: JSON.stringify({}),
      });
      assert.equal(response.status, 401);
    });

    test('returns 422 if other user with same email exists', async function (assert) {
      let user = this.server.create('user', { email: 'foo@skylines.aero' });
      this.server.create('mirage-session', { user });

      this.server.create('user', { email: 'bar@skylines.aero' });

      let response = await fetch('/api/settings', {
        method: 'POST',
        body: JSON.stringify({ email: 'bar@skylines.aero' }),
      });
      assert.equal(response.status, 422);
      assert.matchJson(await response.json(), { error: 'email-exists-already' });
    });

    test('updates the current user', async function (assert) {
      let user = this.server.create('user', { firstName: 'John', email: 'foo@skylines.aero' });
      this.server.create('mirage-session', { user });

      assert.strictEqual(user.firstName, 'John');
      assert.strictEqual(user.email, 'foo@skylines.aero');

      let response = await fetch('/api/settings', {
        method: 'POST',
        body: JSON.stringify({ firstName: 'Jane', email: 'bar@skylines.aero' }),
      });
      assert.equal(response.status, 200);
      assert.matchJson(await response.json(), {});

      user.reload();
      assert.strictEqual(user.firstName, 'Jane');
      assert.strictEqual(user.email, 'bar@skylines.aero');
    });
  });
});
