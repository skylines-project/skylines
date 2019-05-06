import { visit, currentURL } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { setupPolly } from 'skylines/tests/helpers/setup-polly';

module('Acceptance | flight upload', function(hooks) {
  setupApplicationTest(hooks);
  setupPolly(hooks, { recordIfMissing: false });

  module('visiting /flights/upload (unauthenticated)', function(hooks) {
    hooks.beforeEach(async function() {
      await visit('/flights/upload');
    });

    test('redirects to the login page', function(assert) {
      assert.equal(currentURL(), '/login');
    });
  });
});
