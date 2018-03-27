import { module, test } from 'qunit';
import { setupApplicationTest } from 'ember-qunit';
import { visit, currentURL } from '@ember/test-helpers';

import { setupPretender } from 'skylines/tests/helpers/setup-pretender';

module('Acceptance | index', function(hooks) {
  setupApplicationTest(hooks);
  setupPretender(hooks);

  hooks.beforeEach(async function(assert) {
    await visit('/');
    assert.equal(currentURL(), '/');
  });

  test('shows a welcome message', function(assert) {
    assert.dom('[data-test-welcome-message]').exists();
  });
});
