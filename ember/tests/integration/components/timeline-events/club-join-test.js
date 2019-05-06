import { render } from '@ember/test-helpers';
import { setupRenderingTest } from 'ember-qunit';
import { module, test } from 'qunit';

import Service from '@ember/service';

import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | timeline events/club join', function(hooks) {
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
      club: {
        id: 42,
        name: 'SFN',
      },
    });

    await this.owner.lookup('service:intl').loadAndSetLocale('en');
  });

  test('renders default text', async function(assert) {
    await render(hbs`{{timeline-events/club-join event=event}}`);

    assert.dom('td:nth-of-type(2) p:nth-of-type(2)').hasText('John Doe joined SFN.');
  });

  test('renders alternate text if actor is current user', async function(assert) {
    this.owner.lookup('service:account').set('user', { id: 1, name: 'John Doe' });

    await render(hbs`{{timeline-events/club-join event=event}}`);

    assert.dom('td:nth-of-type(2) p:nth-of-type(2)').hasText('You joined SFN.');
  });
});
