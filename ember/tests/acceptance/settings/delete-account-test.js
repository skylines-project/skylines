import { module, test } from 'qunit';
import { setupApplicationTest } from 'ember-qunit';
import { visit, click, currentURL, fillIn } from '@ember/test-helpers';

import { authenticateSession, currentSession } from 'ember-simple-auth/test-support';
import { setupPretender } from 'skylines/tests/helpers/setup-pretender';

module('Acceptance | Settings | Delete Account', function(hooks) {
  setupApplicationTest(hooks);
  setupPretender(hooks);

  function isAuthenticated() {
    return Boolean(currentSession().data.authenticated.settings);
  }

  test('users can delete their accounts on the setting page', async function(assert) {
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

    this.server.get('/api/settings', function() {
      return [200, { 'Content-Type': 'application/json' }, JSON.stringify(settings)];
    });

    this.server.post('/api/users/check-email', function() {
      return [200, { 'Content-Type': 'application/json' }, JSON.stringify({ result: 'self' })];
    });

    this.server.post('/api/settings/password/check', function(request) {
      let json = JSON.parse(request.requestBody);
      let result = json.password === 'secret123';
      return [200, { 'Content-Type': 'application/json' }, JSON.stringify({ result })];
    });

    this.server.delete('/api/account', function(request) {
      let json = JSON.parse(request.requestBody);

      assert.equal(json.password, 'secret123');
      assert.step('account-deleted');

      return [200, { 'Content-Type': 'application/json' }, JSON.stringify({})];
    });

    await authenticateSession({ settings });
    assert.ok(isAuthenticated());

    // visit the front page
    await visit('/');

    // open the menu
    await click('[data-test-nav-bar] [data-test-user-menu-toggle]');
    assert.dom('[data-test-nav-bar] [data-test-user-menu] [data-test-setting-link]').isVisible();

    // click on the "Settings" link
    await click('[data-test-nav-bar] [data-test-user-menu] [data-test-setting-link]');
    assert.equal(currentURL(), '/settings/profile');

    // click on the "Delete Account" button
    await click('[data-test-delete-account-button]');
    assert.dom('[data-test-delete-account-modal]').isVisible();
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .form-group').doesNotHaveClass('has-error');
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .help-block').doesNotExist();
    assert.dom('[data-test-delete-account-modal] [data-test-submit-button]').isDisabled();

    // enter incorrect password
    await fillIn('[data-test-delete-account-modal] [data-test-password-form] input', 'foo');
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .form-group').hasClass('has-error');
    assert.dom('[data-test-delete-account-modal] [data-test-password-form] .help-block').isVisible();
    assert.dom('[data-test-delete-account-modal] [data-test-submit-button]').isDisabled();

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
