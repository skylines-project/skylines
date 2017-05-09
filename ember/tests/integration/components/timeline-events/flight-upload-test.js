import Ember from 'ember';

import { expect } from 'chai';
import { describe, it, beforeEach } from 'mocha';
import { setupComponentTest } from 'ember-mocha';
import hbs from 'htmlbars-inline-precompile';
import { find } from 'ember-native-dom-helpers';

import instanceInitializer from 'skylines/instance-initializers/ember-intl';

describe('Integration | Component | timeline events/flight upload', function() {
  setupComponentTest('timeline-events/flight-upload', { integration: true });

  beforeEach(function() {
    instanceInitializer.initialize(this);

    this.register('service:account', Ember.Service.extend({
      user: null,
      club: null,
    }));

    this.inject.service('intl', { as: 'intl' });
    this.inject.service('account', { as: 'account' });

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

    return this.get('intl').loadAndSetLocale('en');
  });

  it('renders default text', function() {
    this.render(hbs`{{timeline-events/flight-upload event=event}}`);

    expect(find('td:nth-of-type(2) p:nth-of-type(2)').textContent.trim())
      .to.match(/John Doe uploaded a 123 km flight on [\d/]+./);
  });

  it('renders alternate text if actor is current user', function() {
    this.set('account.user', { id: 1, name: 'John Doe' });

    this.render(hbs`{{timeline-events/flight-upload event=event}}`);

    expect(find('td:nth-of-type(2) p:nth-of-type(2)').textContent.trim())
      .to.match(/You uploaded a 123 km flight on [\d/]+./);
  });
});
