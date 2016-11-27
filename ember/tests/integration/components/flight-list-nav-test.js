import Ember from 'ember';

import { expect } from 'chai';
import { setupComponentTest } from 'ember-mocha';
import { beforeEach, it, describe } from 'mocha';
import hbs from 'htmlbars-inline-precompile';

import instanceInitializer from '../../../instance-initializers/ember-intl';

describe('Integration: FlightListNavComponent', function() {
  setupComponentTest('flight-list-nav', { integration: true });

  beforeEach(function() {
    instanceInitializer.initialize(this);

    this.register('service:account', Ember.Service.extend({
      user: null,
      club: null,
    }));

    this.register('service:pinned-flights', Ember.Service.extend({
      pinned: [],
    }));

    this.inject.service('intl', { as: 'intl' });
    this.inject.service('account', { as: 'account' });
    this.inject.service('pinned-flights', { as: 'pinned' });

    this.get('intl').setLocale(['en']);
  });

  it('renders default view', function() {
    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(2);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
  });

  it('shows date', function() {
    this.render(hbs`{{flight-list-nav date="2016-06-24"}}`);
    expect(this.$('li')).to.have.length(4);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('6/24/2016');
    expect(this.$('li:nth-child(4)').text().trim()).to.equal('');
  });

  it('shows date in "latest" mode', function() {
    this.render(hbs`{{flight-list-nav date="2016-06-24" latest=true}}`);
    expect(this.$('li')).to.have.length(4);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('6/24/2016');
    expect(this.$('li:nth-child(4)').text().trim()).to.equal('');
  });

  it('shows selected airport', function() {
    this.set('airport', { id: 123, name: 'Meiersberg' });

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(3);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('Meiersberg');
  });

  it('shows selected club', function() {
    this.set('club', { id: 3, name: 'SFN' });

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(3);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('SFN');
  });

  it('shows own club', function() {
    this.set('account.club', { id: 42, name: 'SFZ Aachen' });

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(3);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('SFZ Aachen');
  });

  it('shows selected club and own club', function() {
    this.set('club', { id: 3, name: 'SFN' });
    this.set('account.club', { id: 42, name: 'SFZ Aachen' });

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(4);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('SFN');
    expect(this.$('li:nth-child(4)').text().trim()).to.equal('SFZ Aachen');
  });

  it('shows club just once if selected club equals own club', function() {
    this.set('club', { id: 42, name: 'SFZ Aachen' });
    this.set('account.club', { id: 42, name: 'SFZ Aachen' });

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(3);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('SFZ Aachen');
  });

  it('shows selected pilot', function() {
    this.set('pilot', { id: 5, name: 'foobar' });

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(3);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('foobar');
  });

  it('shows own user (and unassigned flights link)', function() {
    this.set('account.user', { id: 42, name: 'john doe' });

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(4);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('john doe');
    expect(this.$('li:nth-child(4)').text().trim()).to.equal('Unassigned');
  });

  it('shows selected pilot and own user', function() {
    this.set('pilot', { id: 3, name: 'SFN' });
    this.set('account.user', { id: 42, name: 'john doe' });

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(5);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('SFN');
    expect(this.$('li:nth-child(4)').text().trim()).to.equal('john doe');
    expect(this.$('li:nth-child(5)').text().trim()).to.equal('Unassigned');
  });

  it('shows pilot just once if selected pilot equals own user', function() {
    this.set('pilot', { id: 42, name: 'john doe' });
    this.set('account.user', { id: 42, name: 'john doe' });

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(4);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('john doe');
    expect(this.$('li:nth-child(4)').text().trim()).to.equal('Unassigned');
  });

  it('shows pinned flights if available', function() {
    this.set('pinned.pinned', [1, 2, 3]);

    this.render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);
    expect(this.$('li')).to.have.length(3);
    expect(this.$('li:nth-child(1)').text().trim()).to.equal('All');
    expect(this.$('li:nth-child(2)').text().trim()).to.equal('Latest');
    expect(this.$('li:nth-child(3)').text().trim()).to.equal('Pinned');
  });
});
