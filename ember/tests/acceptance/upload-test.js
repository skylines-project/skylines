import { module, test } from 'qunit';
import { setupApplicationTest } from 'ember-qunit';
import { visit, currentURL } from '@ember/test-helpers';

import { setupPretender } from 'skylines/tests/helpers/setup-pretender';

module('Acceptance | flight upload', function(hooks) {
  setupApplicationTest(hooks);
  setupPretender(hooks);

  module('visiting /flights/upload (unauthenticated)', function(hooks) {
    hooks.beforeEach(async function() {
      await visit('/flights/upload');
    });

    test('redirects to the login page', function(assert) {
      assert.equal(currentURL(), '/login');
    });
  });
});
