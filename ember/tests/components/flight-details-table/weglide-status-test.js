import { render } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';
import { module, test } from 'qunit';

import config from 'skylines/config/environment';
import * as MockFlight from 'skylines/mirage/vcr/flights/87296';

import { setupRenderingTest } from '../../test-helpers';

module('Component | FlightDetailsTable | WeGlide status', function (hooks) {
  setupRenderingTest(hooks);

  hooks.beforeEach(async function () {
    await this.owner.lookup('service:intl').loadAndSetLocale('en');
  });

  test('the WeGlide button is not shown by default', async function (assert) {
    this.flight = deepClone(MockFlight.EXTENDED.flight);

    await render(hbs`<FlightDetailsTable @flight={{this.flight}} />`);
    assert.dom('[data-test-weglide-button]').doesNotExist();
    assert.dom('[data-test-weglide-in-progress]').doesNotExist();
    assert.dom('[data-test-weglide-warning]').doesNotExist();
  });

  test('the WeGlide button is shown for 201 status and if ID is available', async function (assert) {
    this.flight = deepClone(MockFlight.EXTENDED.flight);
    this.flight.igcFile.weglideStatus = 201;
    this.flight.igcFile.weglideData = [{ id: 123 }];

    await render(hbs`<FlightDetailsTable @flight={{this.flight}} />`);
    assert
      .dom('[data-test-weglide-button]')
      .hasAttribute('href', `${config.WeGlide.web}/flights/123`)
      .hasAttribute('target', '_blank');
    assert.dom('[data-test-weglide-in-progress]').doesNotExist();
    assert.dom('[data-test-weglide-warning]').doesNotExist();
  });

  test('the WeGlide button is not shown for while queued', async function (assert) {
    this.flight = deepClone(MockFlight.EXTENDED.flight);
    this.flight.igcFile.weglideStatus = 1;

    await render(hbs`<FlightDetailsTable @flight={{this.flight}} />`);
    assert.dom('[data-test-weglide-button]').doesNotExist();
    assert.dom('[data-test-weglide-in-progress]').exists();
    assert.dom('[data-test-weglide-warning]').doesNotExist();
  });

  test('the WeGlide button is not shown if upload errored', async function (assert) {
    this.flight = deepClone(MockFlight.EXTENDED.flight);
    this.flight.igcFile.weglideStatus = 2;

    await render(hbs`<FlightDetailsTable @flight={{this.flight}} />`);
    assert.dom('[data-test-weglide-button]').doesNotExist();
    assert.dom('[data-test-weglide-in-progress]').doesNotExist();
    assert.dom('[data-test-weglide-warning]').exists();
  });
});

function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}
