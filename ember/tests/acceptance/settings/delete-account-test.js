import { visit, click, currentURL, fillIn, waitFor } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { percySnapshot } from 'ember-percy';
import { authenticateSession, currentSession } from 'ember-simple-auth/test-support';

import { setupPolly } from 'skylines/tests/helpers/setup-polly';

module('Acceptance | Settings | Delete Account', function(hooks) {
  setupApplicationTest(hooks);
  setupPolly(hooks, { recordIfMissing: false });

  function isAuthenticated() {
    return Boolean(currentSession().data.authenticated.settings);
  }

  test('users can delete their accounts on the setting page', async function(assert) {
    let { server } = this.polly;

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

    server.get('/api/settings').intercept((req, res) => {
      res.status(200);
      res.json(settings);
    });

    server.post('/api/users/check-email').intercept((req, res) => {
      res.status(200);
      res.json({ result: 'self' });
    });

    server.post('/api/settings/password/check').intercept((req, res) => {
      let json = JSON.parse(req.body);
      let result = json.password === 'secret123';
      res.status(200);
      res.json({ result });
    });

    server.delete('/api/account').intercept((req, res) => {
      let json = JSON.parse(req.body);

      assert.equal(json.password, 'secret123');
      assert.step('account-deleted');

      res.status(200);
      res.json({});
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
