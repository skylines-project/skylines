import { visit, click, currentURL, fillIn, waitFor } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { setupMirage } from 'ember-cli-mirage/test-support';
import { percySnapshot } from 'ember-percy';
import { authenticateSession, currentSession } from 'ember-simple-auth/test-support';

module('Acceptance | Settings | Delete Account', function (hooks) {
  setupApplicationTest(hooks);
  setupMirage(hooks);

  function isAuthenticated() {
    return Boolean(currentSession().data.authenticated.settings);
  }

  test('users can delete their accounts on the setting page', async function (assert) {
    let { server } = this;

    let settings = {
      id: 123,
      firstName: 'John',
      lastName: 'Doe',
      name: 'John Doe',
      email: 'john@doe.com',

      altitudeUnit: 0,
      distanceUnit: 1,
      liftUnit: 0,
      speedUnit: 1,
    };

    server.get('/api/settings', settings);

    server.post('/api/users/check-email', { result: 'self' });

    server.post('/api/settings/password/check', function (schema, request) {
      let json = JSON.parse(request.requestBody);
      return { result: json.password === 'secret123' };
    });

    server.delete('/api/account', function (schema, request) {
      let json = JSON.parse(request.requestBody);

      assert.equal(json.password, 'secret123');
      assert.step('account-deleted');

      return {};
    });

    await authenticateSession({ settings });
    assert.ok(isAuthenticated());

    // visit the front page
    await visit('/');
    await percySnapshot('Index');

    // open the menu
    await click('[data-test-nav-bar] [data-test-user-menu-dropdown] [data-test-toggle]');
    await waitFor('[data-test-nav-bar] [data-test-user-menu-dropdown] [role="menu"]');

    // click on the "Settings" link
    await click('[data-test-nav-bar] [data-test-user-menu-dropdown] [role="menu"] [data-test-setting-link]');
    assert.equal(currentURL(), '/settings/profile');
    await percySnapshot('Settings');

    // click on the "Delete Account" button
    await click('[data-test-delete-account-button]');
    assert.dom('[data-test-delete-account-modal] .modal-dialog').isVisible();
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .form-group').doesNotHaveClass('has-error');
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .help-block').doesNotExist();
    assert.dom('[data-test-delete-account-modal] [data-test-submit-button]').isDisabled();

    // enter incorrect password
    await fillIn('[data-test-delete-account-modal] [data-test-password-form] input', 'foo');
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .form-group').hasClass('has-error');
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .help-block').isVisible();
    assert.dom('[data-test-delete-account-modal] [data-test-submit-button]').isDisabled();
    await percySnapshot('Delete Account Modal');

    // enter correct password
    await fillIn('[data-test-delete-account-modal] [data-test-password-form] input', 'secret123');
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .form-group').hasClass('has-success');
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .help-block').doesNotExist();
    assert.dom('[data-test-delete-account-modal] [data-test-submit-button]').isNotDisabled();
    assert.ok(isAuthenticated());

    // click "Delete Account" confirmation button
    await click('[data-test-delete-account-modal] [data-test-submit-button]');
    assert.verifySteps(['account-deleted']);
    assert.notOk(isAuthenticated());
  });
});
