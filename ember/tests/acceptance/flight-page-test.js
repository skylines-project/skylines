import { visit } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { percySnapshot } from 'ember-percy';

import { setupPolly } from 'skylines/tests/helpers/setup-polly';

module('Acceptance | Flight Page', function(hooks) {
  setupApplicationTest(hooks);
  setupPolly(hooks);

  test('it works', async function(assert) {
    await visit('/flights/87296');
    await percySnapshot('Flight Page');
    assert.dom('[data-test-pilot-names]').hasText('Tobias Bieniek');
  });
});
