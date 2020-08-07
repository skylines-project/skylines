import { visit } from '@ember/test-helpers';
import { module, test } from 'qunit';

import { percySnapshot } from 'ember-percy';

import * as MockFlight from 'skylines/mirage/vcr/flights/87296';

import { setupApplicationTest } from '../test-helpers';

module('Acceptance | Flight Page', function (hooks) {
  setupApplicationTest(hooks);

  test('it works', async function (assert) {
    this.server.get('/api/flights/87296/json', MockFlight.JSON);
    this.server.get('/api/flights/87296', MockFlight.EXTENDED);

    await visit('/flights/87296');
    await percySnapshot('Flight Page');
    assert.dom('[data-test-pilot-names]').hasText('Tobias Bieniek');
  });
});
