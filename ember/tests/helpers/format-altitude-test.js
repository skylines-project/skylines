import { render, settled } from '@ember/test-helpers';
import { setupRenderingTest } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';
import { module, test } from 'qunit';

module('Helper | format-altitude', function (hooks) {
  setupRenderingTest(hooks);

  test('returns a formatted altitude value', async function (assert) {
    this.set('altitude', 1234);

    await render(hbs`{{format-altitude altitude}}`);
    assert.dom().hasText('1,234 m');

    this.set('altitude', 2345);
    await settled();
    assert.dom().hasText('2,345 m');
  });

  test('supports a `decimals` option', async function (assert) {
    this.set('altitude', 1234);

    await render(hbs`{{format-altitude altitude decimals=2}}`);
    assert.dom().hasText('1,234.00 m');
  });

  test('supports a `withUnit` option', async function (assert) {
    this.set('altitude', 1234);

    await render(hbs`{{format-altitude altitude withUnit=false}}`);
    assert.dom().hasText('1,234');
  });

  test('changing the unit invalidates the value', async function (assert) {
    this.set('altitude', 1234);

    await render(hbs`{{format-altitude altitude}}`);
    assert.dom().hasText('1,234 m');

    this.owner.lookup('service:units').altitudeUnit = 'ft';
    await settled();
    assert.dom().hasText('4,049 ft');
  });

  test('changing the locale invalidates the value', async function (assert) {
    this.set('altitude', 1234);

    await render(hbs`{{format-altitude altitude}}`);
    assert.dom().hasText('1,234 m');

    this.owner.lookup('service:intl').setLocale('de');
    await settled();
    assert.dom().hasText('1.234 m');
  });
});
