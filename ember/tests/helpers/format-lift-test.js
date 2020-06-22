import { render, settled } from '@ember/test-helpers';
import { setupRenderingTest } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';
import { module, test } from 'qunit';

module('Helper | format-lift', function (hooks) {
  setupRenderingTest(hooks);

  test('returns a formatted lift value', async function (assert) {
    this.set('lift', 4.2);

    await render(hbs`{{format-lift lift}}`);
    assert.dom().hasText('4.2 m/s');

    this.set('lift', 1.54);
    await settled();
    assert.dom().hasText('1.5 m/s');
  });

  test('supports a `decimals` option', async function (assert) {
    this.set('lift', 4.2);

    await render(hbs`{{format-lift lift decimals=2}}`);
    assert.dom().hasText('4.20 m/s');
  });

  test('supports a `withUnit` option', async function (assert) {
    this.set('lift', 4.2);

    await render(hbs`{{format-lift lift withUnit=false}}`);
    assert.dom().hasText('4.2');
  });

  test('changing the unit invalidates the value', async function (assert) {
    this.set('lift', 4.2);

    await render(hbs`{{format-lift lift}}`);
    assert.dom().hasText('4.2 m/s');

    this.owner.lookup('service:units').liftUnit = 'ft/min';
    await settled();
    assert.dom().hasText('827 ft/min');
  });

  test('changing the locale invalidates the value', async function (assert) {
    this.set('lift', 4.2);

    await render(hbs`{{format-lift lift}}`);
    assert.dom().hasText('4.2 m/s');

    this.owner.lookup('service:intl').setLocale('de');
    await settled();
    assert.dom().hasText('4,2 m/s');
  });
});
