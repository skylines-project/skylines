import { visit, currentURL } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { setupMirage } from 'ember-cli-mirage/test-support';

module('Acceptance | page-not-found', function (hooks) {
  setupApplicationTest(hooks);
  setupMirage(hooks);

  hooks.beforeEach(async function () {
    await visit('/foobar');
  });

  test('will keep the URL at /foobar', function (assert) {
    assert.equal(currentURL(), '/foobar');
  });

  test('will show "Page not found" error message', function (assert) {
    assert.dom('.page-header').containsText('Page not found');
  });
});
