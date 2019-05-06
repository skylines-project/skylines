import { render } from '@ember/test-helpers';
import { setupRenderingTest } from 'ember-qunit';
import { module, test } from 'qunit';

import Service from '@ember/service';

import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | timeline events/flight upload', function(hooks) {
  setupRenderingTest(hooks);

  hooks.beforeEach(async function() {
    this.owner.setupRouter();

    this.owner.register(
      'service:account',
      Service.extend({
        user: null,
        club: null,
      }),
    );

    this.set('event', {
      time: '2016-06-24T12:34:56Z',
      actor: {
        id: 1,
        name: 'John Doe',
      },
      flight: {
        id: 42,
        date: '2016-01-31',
        distance: 123456,
        pilot_id: 5,
        copilot_id: null,
      },
    });

    await this.owner.lookup('service:intl').loadAndSetLocale('en');
  });

  test('renders default text', async function(assert) {
    await render(hbs`{{timeline-events/flight-upload event=event}}`);

    assert.dom('td:nth-of-type(2) p:nth-of-type(2)').hasText(/John Doe uploaded a 123 km flight on [\d/]+./);
  });

  test('renders alternate text if actor is current user', async function(assert) {
    this.owner.lookup('service:account').set('user', { id: 1, name: 'John Doe' });

    await render(hbs`{{timeline-events/flight-upload event=event}}`);

    assert.dom('td:nth-of-type(2) p:nth-of-type(2)').hasText(/You uploaded a 123 km flight on [\d/]+./);
  });
});
