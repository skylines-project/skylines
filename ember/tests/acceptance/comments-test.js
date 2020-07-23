import { click, fillIn, visit } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';
import { module, test } from 'qunit';

import { setupMirage } from 'ember-cli-mirage/test-support';
import { authenticateSession } from 'ember-simple-auth/test-support';

import * as MockFlight from 'skylines/mirage/vcr/flights/87296';

module('Acceptance | Comments', function (hooks) {
  setupApplicationTest(hooks);
  setupMirage(hooks);

  module('unauthenticated', function () {
    test('shows existing comments', async function (assert) {
      this.server.get('/api/flights/87296/json', MockFlight.JSON);
      this.server.get('/api/flights/87296', MockFlight.EXTENDED);

      await visit('/flights/87296');
      await click('[data-test-sidebar-tab="comments"]');
      assert.dom('[data-test-comment]').exists({ count: 1 });
      assert.dom('[data-test-comment]').hasText('Jane Doe:\xa0 8-o');
      assert.dom('[data-test-add-comment]').doesNotExist();
    });
  });

  module('authenticated', function (hooks) {
    hooks.beforeEach(async function () {
      await authenticateSession({
        settings: {
          altitudeUnit: 0,
          club: null,
          distanceUnit: 1,
          email: 'johnny.dee@gmail.com',
          firstName: 'John',
          followers: 107,
          following: 128,
          id: 1,
          lastName: 'Doe',
          liftUnit: 0,
          name: 'John Doe',
          speedUnit: 1,
          trackingCallsign: 'JD',
          trackingDelay: 0,
          trackingKey: 'ABCDEF42',
        },
      });
    });

    test('shows existing comments and can add a new comment', async function (assert) {
      this.server.get('/api/flights/87296/json', MockFlight.JSON);
      this.server.get('/api/flights/87296', MockFlight.EXTENDED);

      this.server.post('/api/flights/87296/comments', function (schema, request) {
        let payload = JSON.parse(request.requestBody);
        assert.step(`add-comment(${payload.text})`);
      });

      await visit('/flights/87296');
      await click('[data-test-sidebar-tab="comments"]');
      assert.dom('[data-test-comment]').exists({ count: 1 });
      assert.dom('[data-test-comment]').hasText('Jane Doe:\xa0 8-o');
      assert.dom('[data-test-add-comment]').exists();

      await fillIn('[data-test-add-comment] [data-test-input]', 'This is a great flight! 🎉');
      await click('[data-test-add-comment] [data-test-submit]');
      assert.dom('[data-test-comment]').exists({ count: 2 });
      assert.dom('[data-test-comment="0"]').hasText('Jane Doe:\xa0 8-o');
      assert.dom('[data-test-comment="1"]').hasText('John Doe:\xa0 This is a great flight! 🎉');

      assert.dom('[data-test-add-comment] [data-test-input]').hasValue('');

      assert.verifySteps(['add-comment(This is a great flight! 🎉)']);
    });

    test('error case', async function (assert) {
      this.server.get('/api/flights/87296/json', MockFlight.JSON);
      this.server.get('/api/flights/87296', MockFlight.EXTENDED);

      this.server.post('/api/flights/87296/comments', {}, 500);

      await visit('/flights/87296');
      await click('[data-test-sidebar-tab="comments"]');
      assert.dom('[data-test-comment]').exists({ count: 1 });
      assert.dom('[data-test-comment]').hasText('Jane Doe:\xa0 8-o');
      assert.dom('[data-test-add-comment]').exists();

      await fillIn('[data-test-add-comment] [data-test-input]', 'This is a great flight! 🎉');
      await click('[data-test-add-comment] [data-test-submit]');
      assert
        .dom('[data-test-notification-message]')
        .hasText('An error occured while adding your comment. Please try again later.');

      assert.dom('[data-test-comment]').exists({ count: 1 });
      assert.dom('[data-test-comment]').hasText('Jane Doe:\xa0 8-o');

      assert.dom('[data-test-add-comment] [data-test-input]').hasValue('This is a great flight! 🎉');
    });
  });
});
