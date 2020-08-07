import { visit, currentURL } from '@ember/test-helpers';
import { module, test } from 'qunit';

import { setupApplicationTest } from '../test-helpers';

module('Acceptance | page-not-found', function (hooks) {
  setupApplicationTest(hooks);

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
