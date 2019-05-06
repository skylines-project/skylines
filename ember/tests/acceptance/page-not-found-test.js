import { visit, currentURL } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { setupPolly } from 'skylines/tests/helpers/setup-polly';

module('Acceptance | page-not-found', function(hooks) {
  setupApplicationTest(hooks);
  setupPolly(hooks, { recordIfMissing: false });

  hooks.beforeEach(async function() {
    await visit('/foobar');
  });

  test('will keep the URL at /foobar', function(assert) {
    assert.equal(currentURL(), '/foobar');
  });

  test('will show "Page not found" error message', function(assert) {
    assert.dom('.page-header').containsText('Page not found');
  });
});
