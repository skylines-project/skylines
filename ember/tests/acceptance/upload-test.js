import { visit, currentURL } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { setupMirage } from 'ember-cli-mirage/test-support';

module('Acceptance | flight upload', function (hooks) {
  setupApplicationTest(hooks);
  setupMirage(hooks);

  test('unauthenticated visit redirects to the login page', async function (assert) {
    await visit('/flights/upload');
    assert.equal(currentURL(), '/login');
  });
});
