import { render, findAll } from '@ember/test-helpers';
import { setupRenderingTest } from 'ember-qunit';
import { module, test } from 'qunit';

import Service from '@ember/service';

import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | flight list nav', function(hooks) {
  setupRenderingTest(hooks);

  hooks.beforeEach(async function() {
    this.owner.register(
      'service:account',
      Service.extend({
        user: null,
        club: null,
      }),
    );

    this.owner.register(
      'service:pinned-flights',
      Service.extend({
        // eslint-disable-next-line ember/avoid-leaking-state-in-ember-objects
        pinned: [],
      }),
    );

    await this.owner.lookup('service:intl').loadAndSetLocale('en');
  });

  test('renders default view', async function(assert) {
    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 2);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
  });

  test('shows date', async function(assert) {
    await render(hbs`{{flight-list-nav date="2016-06-24"}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 4);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('  ');
    assert.dom(elements[2]).hasText(/0?6\/24\/2016/);
    assert.dom(elements[3]).hasText('  ');
  });

  test('shows date in "latest" mode', async function(assert) {
    await render(hbs`{{flight-list-nav date="2016-06-24" latest=true}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 4);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('  ');
    assert.dom(elements[2]).hasText(/0?6\/24\/2016/);
    assert.dom(elements[3]).hasText('  ');
  });

  test('shows selected airport', async function(assert) {
    this.set('airport', { id: 123, name: 'Meiersberg' });

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 3);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('Meiersberg');
  });

  test('shows selected club', async function(assert) {
    this.set('club', { id: 3, name: 'SFN' });

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 3);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('SFN');
  });

  test('shows own club', async function(assert) {
    this.owner.lookup('service:account').set('club', { id: 42, name: 'SFZ Aachen' });

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 3);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('SFZ Aachen');
  });

  test('shows selected club and own club', async function(assert) {
    this.set('club', { id: 3, name: 'SFN' });
    this.owner.lookup('service:account').set('club', { id: 42, name: 'SFZ Aachen' });

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 4);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('SFN');
    assert.dom(elements[3]).hasText('SFZ Aachen');
  });

  test('shows club just once if selected club equals own club', async function(assert) {
    this.set('club', { id: 42, name: 'SFZ Aachen' });
    this.owner.lookup('service:account').set('club', { id: 42, name: 'SFZ Aachen' });

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 3);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('SFZ Aachen');
  });

  test('shows selected pilot', async function(assert) {
    this.set('pilot', { id: 5, name: 'foobar' });

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 3);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('foobar');
  });

  test('shows own user (and unassigned flights link)', async function(assert) {
    this.owner.lookup('service:account').set('user', { id: 42, name: 'john doe' });

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 4);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('john doe');
    assert.dom(elements[3]).hasText('Unassigned');
  });

  test('shows selected pilot and own user', async function(assert) {
    this.set('pilot', { id: 3, name: 'SFN' });
    this.owner.lookup('service:account').set('user', { id: 42, name: 'john doe' });

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 5);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('SFN');
    assert.dom(elements[3]).hasText('john doe');
    assert.dom(elements[4]).hasText('Unassigned');
  });

  test('shows pilot just once if selected pilot equals own user', async function(assert) {
    this.set('pilot', { id: 42, name: 'john doe' });
    this.owner.lookup('service:account').set('user', { id: 42, name: 'john doe' });

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 4);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('john doe');
    assert.dom(elements[3]).hasText('Unassigned');
  });

  test('shows pinned flights if available', async function(assert) {
    this.owner.lookup('service:pinned-flights').set('pinned', [1, 2, 3]);

    await render(hbs`{{flight-list-nav date=date airport=airport club=club pilot=pilot}}`);

    let elements = findAll('li');
    assert.equal(elements.length, 3);
    assert.dom(elements[0]).hasText('All');
    assert.dom(elements[1]).hasText('Latest  ');
    assert.dom(elements[2]).hasText('Pinned');
  });
});
