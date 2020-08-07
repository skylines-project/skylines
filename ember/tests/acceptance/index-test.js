import { visit, currentURL } from '@ember/test-helpers';
import { module, test } from 'qunit';

import { setupApplicationTest } from '../test-helpers';

module('Acceptance | index', function (hooks) {
  setupApplicationTest(hooks);

  hooks.beforeEach(async function (assert) {
    await visit('/');
    assert.equal(currentURL(), '/');
  });

  test('shows a welcome message', function (assert) {
    assert.dom('[data-test-welcome-message]').exists();
  });
});
