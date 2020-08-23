import { visit, currentURL, click, fillIn } from '@ember/test-helpers';
import { module, test } from 'qunit';

import { Response } from 'ember-cli-mirage';

import { setupApplicationTest } from '../test-helpers';
import { authenticateAs } from '../test-helpers/auth';

module('Acceptance | Password Recovery', function (hooks) {
  setupApplicationTest(hooks);

  module('Step 1', function () {
    test('Password recovery email can be requested', async function (assert) {
      let user = this.server.create('user', { email: 'johnny@dee.com' });

      await visit('/users/recover');
      assert.equal(currentURL(), '/users/recover');
      assert.dom('[data-test-submit-button]').isDisabled();

      await fillIn('[data-test-email-input] input', 'test');
      assert
        .dom('[data-test-email-input] [data-test-validation-message]')
        .hasText('Email address must be a valid email address');
      assert.dom('[data-test-submit-button]').isDisabled();

      await fillIn('[data-test-email-input] input', 'foo@bar.com');
      assert.dom('[data-test-email-input] [data-test-validation-message]').hasText('This email address is unknown.');
      assert.dom('[data-test-submit-button]').isDisabled();

      await fillIn('[data-test-email-input] input', 'johnny@dee.com');
      assert.dom('[data-test-email-input] [data-test-validation-message]').doesNotExist();
      assert.dom('[data-test-submit-button]').isNotDisabled();

      await click('[data-test-submit-button]');
      assert.dom('[data-test-success-message]').exists();
      assert.equal(currentURL(), '/users/recover');

      user.reload();
      assert.ok(user.recoveryKey);
    });

    test('Admin users can request password recovery links', async function (assert) {
      let admin = this.server.create('user', { admin: true });
      let user = this.server.create('user', { email: 'johnny@dee.com' });

      await authenticateAs(admin);

      await visit('/users/recover');
      await fillIn('[data-test-email-input] input', 'johnny@dee.com');
      await click('[data-test-submit-button]');
      assert.dom('[data-test-success-message]').includesText('http://skylines.aero/users/recover?key=abc123def');
      assert.equal(currentURL(), '/users/recover');

      user.reload();
      assert.ok(user.recoveryKey);
    });

    test('Errors are shown', async function (assert) {
      this.server.create('user', { email: 'johnny@dee.com' });

      this.server.post('/api/users/recover', () => new Response(503, {}, { error: 'mail-service-unavailable' }));

      await visit('/users/recover');
      await fillIn('[data-test-email-input] input', 'johnny@dee.com');
      await click('[data-test-submit-button]');
      assert.dom('[data-test-error-message]').hasText('Error: Request was rejected due to server error');
      assert.dom('[data-test-success-message]').doesNotExist();
    });
  });

  module('Step 2', function () {
    test('Password can be reset', async function (assert) {
      let user = this.server.create('user', { recoveryKey: 'secret123' });

      await visit('/users/recover?key=secret123');
      assert.equal(currentURL(), '/users/recover?key=secret123');
      assert.dom('[data-test-submit-button]').isDisabled();

      await fillIn('[data-test-password-input] input', 'johnny');
      await fillIn('[data-test-password-confirmation-input] input', 'j');
      assert
        .dom('[data-test-password-confirmation-input] [data-test-validation-message]')
        .hasText('Passwords do not match');
      assert.dom('[data-test-submit-button]').isDisabled();

      await fillIn('[data-test-password-confirmation-input] input', 'johnny');
      assert.dom('[data-test-password-confirmation-input] [data-test-validation-message]').doesNotExist();
      assert.dom('[data-test-submit-button]').isNotDisabled();

      await click('[data-test-submit-button]');
      assert.dom('[data-test-success-message]').exists();
      assert.equal(currentURL(), '/users/recover?key=secret123');

      user.reload();
      assert.equal(user.password, 'johnny');
    });

    test('Errors are shown', async function (assert) {
      await visit('/users/recover?key=secret123');
      assert.equal(currentURL(), '/users/recover?key=secret123');
      assert.dom('[data-test-submit-button]').isDisabled();

      await fillIn('[data-test-password-input] input', 'johnny');
      await fillIn('[data-test-password-confirmation-input] input', 'johnny');
      assert.dom('[data-test-password-confirmation-input] [data-test-validation-message]').doesNotExist();
      assert.dom('[data-test-submit-button]').isNotDisabled();

      await click('[data-test-submit-button]');
      assert.dom('[data-test-error-message]').hasText('Error: Request was rejected because it was invalid');
      assert.dom('[data-test-success-message]').doesNotExist();
    });
  });
});
