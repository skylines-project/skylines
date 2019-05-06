import { setupTest } from 'ember-qunit';
import { module, test } from 'qunit';

import Service from '@ember/service';

import { BASE_LAYER_COOKIE_KEY, OVERLAY_LAYERS_COOKIE_KEY } from 'skylines/services/map-settings';

module('Unit | Service | map-settings', function(hooks) {
  setupTest(hooks);

  hooks.beforeEach(function() {
    this.owner.register(
      'service:router',
      Service.extend({
        currentURL: '/',
      }),
    );

    this.owner.register(
      'service:cookies',
      Service.extend({
        read(key) {
          if (key === BASE_LAYER_COOKIE_KEY) {
            return 'Foo';
          } else if (key === OVERLAY_LAYERS_COOKIE_KEY) {
            return 'Bar;Baz';
          }
        },
      }),
    );

    this.subject = () => this.owner.lookup('service:map-settings');
  });

  test('defaults to "OpenStreetMap" and "Airspace"', function(assert) {
    this.owner.register(
      'service:cookies',
      Service.extend({
        read() {},
      }),
    );

    let service = this.subject();
    assert.equal(service.get('baseLayer'), 'OpenStreetMap');
    assert.deepEqual(service.get('overlayLayers'), ['Airspace']);
  });

  test('reads layers from cookies', function(assert) {
    let service = this.subject();
    assert.equal(service.get('baseLayer'), 'Foo');
    assert.deepEqual(service.get('overlayLayers'), ['Bar', 'Baz']);
  });

  test('handles empty overlays cookie correctly', function(assert) {
    this.owner.register(
      'service:cookies',
      Service.extend({
        read(key) {
          if (key === OVERLAY_LAYERS_COOKIE_KEY) {
            return '';
          }
        },
      }),
    );

    let service = this.subject();
    assert.deepEqual(service.get('overlayLayers'), []);
  });

  test('prioritizes layers from query params', function(assert) {
    let router = this.owner.lookup('service:router');

    router.set('currentURL', '/flights/17537?baselayer=alternate&overlays=foo;bar');

    let service = this.subject();
    assert.equal(service.get('baseLayer'), 'alternate');
    assert.deepEqual(service.get('overlayLayers'), ['foo', 'bar']);

    router.set('currentURL', '/flights/17537');

    assert.equal(service.get('baseLayer'), 'Foo');
    assert.deepEqual(service.get('overlayLayers'), ['Bar', 'Baz']);
  });

  test('handles empty overlays query param correctly', function(assert) {
    let router = this.owner.lookup('service:router');
    router.set('currentURL', '/flights/17537?baselayer=alternate&overlays=');

    let service = this.subject();
    assert.deepEqual(service.get('overlayLayers'), []);
  });

  test('isLayerVisible() returns true/false if layer is base layer or enabled overlay layer', function(assert) {
    let service = this.subject();
    assert.strictEqual(service.isLayerVisible('Foo'), true);
    assert.strictEqual(service.isLayerVisible('Bar'), true);
    assert.strictEqual(service.isLayerVisible('Baz'), true);
    assert.strictEqual(service.isLayerVisible('Qux'), false);
  });

  test('setBaseLayer() changes the "baseLayer" and persists it to the cookie', function(assert) {
    assert.expect(4);

    this.owner.register(
      'service:cookies',
      Service.extend({
        read() {},
        write(key, value) {
          assert.equal(key, BASE_LAYER_COOKIE_KEY);
          assert.equal(value, 'foo');
        },
      }),
    );

    let service = this.subject();
    assert.equal(service.get('baseLayer'), 'OpenStreetMap');

    service.setBaseLayer('foo');
    assert.equal(service.get('baseLayer'), 'foo');
  });

  test('toggleOverlayLayer() adds to the existing "overlayLayers" and persists it to the cookie', function(assert) {
    assert.expect(4);

    this.owner.register(
      'service:cookies',
      Service.extend({
        read() {},
        write(key, value) {
          assert.equal(key, OVERLAY_LAYERS_COOKIE_KEY);
          assert.equal(value, 'Airspace;foo');
        },
      }),
    );

    let service = this.subject();
    assert.deepEqual(service.get('overlayLayers'), ['Airspace']);

    service.toggleOverlayLayer('foo');
    assert.deepEqual(service.get('overlayLayers'), ['Airspace', 'foo']);
  });

  test('toggleOverlayLayer() removes from the existing "overlayLayers" and persists it to the cookie', function(assert) {
    assert.expect(4);

    this.owner.register(
      'service:cookies',
      Service.extend({
        read() {},
        write(key, value) {
          assert.equal(key, OVERLAY_LAYERS_COOKIE_KEY);
          assert.equal(value, '');
        },
      }),
    );

    let service = this.subject();
    assert.deepEqual(service.get('overlayLayers'), ['Airspace']);

    service.toggleOverlayLayer('Airspace');
    assert.deepEqual(service.get('overlayLayers'), []);
  });
});
