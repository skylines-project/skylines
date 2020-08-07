import { visit, click, currentURL, fillIn, waitFor } from '@ember/test-helpers';
import { module, test } from 'qunit';

import percySnapshot from '@percy/ember';
import { currentSession } from 'ember-simple-auth/test-support';

import { setupApplicationTest } from '../../test-helpers';
import { authenticateAs } from '../../test-helpers/auth';

module('Acceptance | Settings | Delete Account', function (hooks) {
  setupApplicationTest(hooks);

  function isAuthenticated() {
    return currentSession().isAuthenticated;
  }

  test('users can delete their accounts on the setting page', async function (assert) {
    let { server } = this;

    let user = server.create('user', {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@doe.com',
    });

    await authenticateAs(user);

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
