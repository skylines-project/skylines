import Ember from 'ember';

import { expect } from 'chai';
import { describeComponent, it } from 'ember-mocha';
import { beforeEach } from 'mocha';
import hbs from 'htmlbars-inline-precompile';

import instanceInitializer from '../../../../instance-initializers/ember-intl';

let options = { integration: true };

describeComponent('timeline-events/club-join', 'Integration: ClubJoinTimelineEventComponent', options, function() {
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
      club: {
        id: 42,
        name: 'SFN',
      },
    });
  });

  it('renders default text', function() {
    this.render(hbs`{{timeline-events/club-join event=event}}`);

    expect(this.$('td:nth-of-type(2) p:nth-of-type(2)').text().trim())
      .to.equal('John Doe joined SFN.');
  });

  it('renders alternate text if actor is current user', function() {
    this.set('account.user', { id: 1, name: 'John Doe' });

    this.render(hbs`{{timeline-events/club-join event=event}}`);

    expect(this.$('td:nth-of-type(2) p:nth-of-type(2)').text().trim())
      .to.equal('You joined SFN.');
  });
});
