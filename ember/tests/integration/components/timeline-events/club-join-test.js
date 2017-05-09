import Ember from 'ember';

import { expect } from 'chai';
import { describe, it, beforeEach } from 'mocha';
import { setupComponentTest } from 'ember-mocha';
import hbs from 'htmlbars-inline-precompile';
import { find } from 'ember-native-dom-helpers';

import instanceInitializer from 'skylines/instance-initializers/ember-intl';

describe('Integration | Component | timeline events/club join', function() {
  setupComponentTest('timeline-events/club-join', { integration: true });

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
      club: {
        id: 42,
        name: 'SFN',
      },
    });

    return this.get('intl').loadAndSetLocale('en');
  });

  it('renders default text', function() {
    this.render(hbs`{{timeline-events/club-join event=event}}`);

    expect(find('td:nth-of-type(2) p:nth-of-type(2)').textContent.trim())
      .to.equal('John Doe joined SFN.');
  });

  it('renders alternate text if actor is current user', function() {
    this.set('account.user', { id: 1, name: 'John Doe' });

    this.render(hbs`{{timeline-events/club-join event=event}}`);

    expect(find('td:nth-of-type(2) p:nth-of-type(2)').textContent.trim())
      .to.equal('You joined SFN.');
  });
});
