import { render, settled } from '@ember/test-helpers';
import { setupRenderingTest } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';
import { module, test } from 'qunit';

module('Helper | format-distance', function (hooks) {
  setupRenderingTest(hooks);

  test('returns a formatted distance value', async function (assert) {
    this.set('distance', 42024);

    await render(hbs`{{format-distance distance}}`);
    assert.dom().hasText('42 km');

    this.set('distance', 123456);
    await settled();
    assert.dom().hasText('123 km');
  });

  test('supports a `decimals` option', async function (assert) {
    this.set('distance', 42024);

    await render(hbs`{{format-distance distance decimals=2}}`);
    assert.dom().hasText('42.02 km');
  });

  test('supports a `withUnit` option', async function (assert) {
    this.set('distance', 42024);

    await render(hbs`{{format-distance distance withUnit=false}}`);
    assert.dom().hasText('42');
  });

  test('changing the unit invalidates the value', async function (assert) {
    this.set('distance', 42024);

    await render(hbs`{{format-distance distance}}`);
    assert.dom().hasText('42 km');

    this.owner.lookup('service:units').distanceUnit = 'NM';
    await settled();
    assert.dom().hasText('23 NM');
  });

  test('changing the locale invalidates the value', async function (assert) {
    this.set('distance', 42024);

    await render(hbs`{{format-distance distance decimals=1}}`);
    assert.dom().hasText('42.0 km');

    this.owner.lookup('service:intl').setLocale('de');
    await settled();
    assert.dom().hasText('42,0 km');
  });
});
