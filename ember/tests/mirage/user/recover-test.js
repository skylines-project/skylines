import { module, test } from 'qunit';

import setupMirage from 'ember-cli-mirage/test-support/setup-mirage';
import fetch from 'fetch';

import { setupTest } from '../../test-helpers';

module('Mirage | User', function (hooks) {
  setupTest(hooks);
  setupMirage(hooks);

  module('POST /api/users/recover', function () {
    module('without `recoveryKey`', function () {
      test('sets the recovery key', async function (assert) {
        let user = this.server.create('user', { email: 'foo@bar.com' });
        assert.notOk(user.recoveryKey);

        let response = await fetch('/api/users/recover', {
          method: 'POST',
          body: JSON.stringify({ email: 'foo@bar.com' }),
        });
        assert.equal(response.status, 201);

        let responsePayload = await response.json();
        assert.matchJson(responsePayload, {});

        user.reload();
        assert.ok(user.recoveryKey);
      });

      test('returns the url if the requesting user is an admin', async function (assert) {
        let admin = this.server.create('user', { admin: true });
        this.server.create('mirage-session', { user: admin });

        let user = this.server.create('user', { email: 'foo@bar.com' });
        assert.notOk(user.recoveryKey);

        let response = await fetch('/api/users/recover', {
          method: 'POST',
          body: JSON.stringify({ email: 'foo@bar.com' }),
        });
        assert.equal(response.status, 201);

        let responsePayload = await response.json();
        assert.matchJson(responsePayload, { url: 'http://skylines.aero/users/recover?key=abc123def' });

        user.reload();
        assert.ok(user.recoveryKey);
      });

      test('returns 422 if `email` field is missing', async function (assert) {
        let user = this.server.create('user', { email: 'foo@bar.com' });
        assert.notOk(user.recoveryKey);

        let response = await fetch('/api/users/recover', {
          method: 'POST',
          body: JSON.stringify({}),
        });
        assert.equal(response.status, 422);

        let responsePayload = await response.json();
        assert.matchJson(responsePayload, { error: 'validation-failed' });

        user.reload();
        assert.notOk(user.recoveryKey);
      });

      test('returns 422 if email is unknown', async function (assert) {
        let response = await fetch('/api/users/recover', {
          method: 'POST',
          body: JSON.stringify({ email: 'foo@bar.com' }),
        });
        assert.equal(response.status, 422);

        let responsePayload = await response.json();
        assert.matchJson(responsePayload, { error: 'email-unknown' });
      });
    });

    module('with `recoveryKey`', function () {
      test('sets the password', async function (assert) {
        let user = this.server.create('user', { recoveryKey: 'secret123' });
        assert.notEqual(user.password, 'foo');

        let response = await fetch('/api/users/recover', {
          method: 'POST',
          body: JSON.stringify({ recoveryKey: 'secret123', password: 'foo' }),
        });
        assert.equal(response.status, 201);

        let responsePayload = await response.json();
        assert.matchJson(responsePayload, {});

        user.reload();
        assert.equal(user.password, 'foo');
        assert.notOk(user.recoveryKey);
      });

      test('returns 422 if `recoveryKey` is unknown', async function (assert) {
        let user = this.server.create('user', { recoveryKey: 'secret123' });
        assert.notEqual(user.password, 'foo');

        let response = await fetch('/api/users/recover', {
          method: 'POST',
          body: JSON.stringify({ recoveryKey: 'foo', password: 'foo' }),
        });
        assert.equal(response.status, 422);

        let responsePayload = await response.json();
        assert.matchJson(responsePayload, { error: 'recovery-key-unknown' });

        user.reload();
        assert.notEqual(user.password, 'foo');
      });

      test('returns 422 if `recoveryKey` is missing', async function (assert) {
        let user = this.server.create('user', { recoveryKey: 'secret123' });
        assert.notEqual(user.password, 'foo');

        let response = await fetch('/api/users/recover', {
          method: 'POST',
          body: JSON.stringify({ password: 'foo' }),
        });
        assert.equal(response.status, 422);

        let responsePayload = await response.json();
        assert.matchJson(responsePayload, { error: 'validation-failed' });

        user.reload();
        assert.notEqual(user.password, 'foo');
      });

      test('returns 422 if `password` is missing', async function (assert) {
        let user = this.server.create('user', { recoveryKey: 'secret123' });
        assert.notEqual(user.password, 'foo');

        let response = await fetch('/api/users/recover', {
          method: 'POST',
          body: JSON.stringify({ recoveryKey: 'secret123' }),
        });
        assert.equal(response.status, 422);

        let responsePayload = await response.json();
        assert.matchJson(responsePayload, { error: 'validation-failed' });

        user.reload();
        assert.notEqual(user.password, 'foo');
      });
    });
  });
});
