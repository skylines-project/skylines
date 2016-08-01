import Ember from 'ember';

import { expect } from 'chai';
import { describeComponent, it } from 'ember-mocha';
import { beforeEach } from 'mocha';
import hbs from 'htmlbars-inline-precompile';

import instanceInitializer from '../../../../instance-initializers/ember-intl';

let options = { integration: true };

describeComponent('timeline-events/follower', 'Integration: FollowerTimelineEventComponent', options, function() {
  beforeEach(function() {
    instanceInitializer.initialize(this);

    this.register('service:account', Ember.Service.extend({
      user: null,
      club: null,
    }));

    this.inject.service('intl', { as: 'intl' });
    this.inject.service('account', { as: 'account' });

    this.get('intl').setLocale('en');

    this.set('event', {
      time: '2016-06-24T12:34:56Z',
      actor: {
        id: 1,
        name: 'John Doe',
      },
      user: {
        id: 42,
        name: 'Jane Doe',
      },
    });
  });

  it('renders default text', function() {
    this.render(hbs`{{timeline-events/follower event=event}}`);

    expect(this.$('td:nth-of-type(2) p:nth-of-type(2)').text().trim())
      .to.equal('John Doe started following Jane Doe.');
  });

  it('renders alternate text if actor is current user', function() {
    this.set('account.user', { id: 1, name: 'John Doe' });

    this.render(hbs`{{timeline-events/follower event=event}}`);

    expect(this.$('td:nth-of-type(2) p:nth-of-type(2)').text().trim())
      .to.equal('You started following Jane Doe.');
  });

  it('renders alternate text if followed user is current user', function() {
    this.set('account.user', { id: 42, name: 'Jane Doe' });

    this.render(hbs`{{timeline-events/follower event=event}}`);

    expect(this.$('td:nth-of-type(2) p:nth-of-type(2)').text().trim())
      .to.equal('John Doe started following you.');
  });
});
