import { visit, currentURL } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { setupMirage } from 'ember-cli-mirage/test-support';

module('Acceptance | flight upload', function (hooks) {
  setupApplicationTest(hooks);
  setupMirage(hooks);

  module('visiting /flights/upload (unauthenticated)', function (hooks) {
    hooks.beforeEach(async function () {
      await visit('/flights/upload');
    });

    test('redirects to the login page', function (assert) {
      assert.equal(currentURL(), '/login');
    });
  });
});
