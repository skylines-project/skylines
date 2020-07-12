import { visit, currentURL } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { setupMirage } from 'ember-cli-mirage/test-support';

module('Acceptance | index', function (hooks) {
  setupApplicationTest(hooks);
  setupMirage(hooks);

  hooks.beforeEach(async function (assert) {
    await visit('/');
    assert.equal(currentURL(), '/');
  });

  test('shows a welcome message', function (assert) {
    assert.dom('[data-test-welcome-message]').exists();
  });
});
