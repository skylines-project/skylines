import { render, settled } from '@ember/test-helpers';
import { setupRenderingTest } from 'ember-qunit';
import hbs from 'htmlbars-inline-precompile';
import { module, test } from 'qunit';

module('Helper | format-speed', function (hooks) {
  setupRenderingTest(hooks);

  test('returns a formatted speed value', async function (assert) {
    this.set('speed', 33.76);

    await render(hbs`{{format-speed speed}}`);
    assert.dom().hasText('121.5 km/h');

    this.set('speed', 54.1);
    await settled();
    assert.dom().hasText('194.8 km/h');
  });

  test('supports a `decimals` option', async function (assert) {
    this.set('speed', 33.76);

    await render(hbs`{{format-speed speed decimals=2}}`);
    assert.dom().hasText('121.54 km/h');
  });

  test('supports a `withUnit` option', async function (assert) {
    this.set('speed', 33.76);

    await render(hbs`{{format-speed speed withUnit=false}}`);
    assert.dom().hasText('121.5');
  });

  test('changing the unit invalidates the value', async function (assert) {
    this.set('speed', 33.76);

    await render(hbs`{{format-speed speed}}`);
    assert.dom().hasText('121.5 km/h');

    this.owner.lookup('service:units').speedUnit = 'm/s';
    await settled();
    assert.dom().hasText('33.8 m/s');
  });

  test('changing the locale invalidates the value', async function (assert) {
    this.set('speed', 33.76);

    await render(hbs`{{format-speed speed}}`);
    assert.dom().hasText('121.5 km/h');

    this.owner.lookup('service:intl').setLocale('de');
    await settled();
    assert.dom().hasText('121,5 km/h');
  });
});
