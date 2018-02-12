import { expect } from 'chai';
import { describe, it } from 'mocha';
import { setupTest } from 'ember-mocha';

import Service from '@ember/service';
import { BASE_LAYER_COOKIE_KEY, OVERLAY_LAYERS_COOKIE_KEY } from 'skylines/services/map-settings';

describe('Unit | Service | map-settings', function() {
  setupTest('service:map-settings', { integration: true });

  beforeEach(function() {
    this.register('service:router', Service.extend({
      currentURL: '/'
    }));

    this.register('service:cookies', Service.extend({
      read(key) {
        if (key === BASE_LAYER_COOKIE_KEY) {
          return 'Foo';
        } else if (key === OVERLAY_LAYERS_COOKIE_KEY) {
          return 'Bar;Baz';
        }
      },
    }));
  });

  it('defaults to "OpenStreetMap" and "Airspace"', function() {
    this.register('service:cookies', Service.extend({
      read() {},
    }));

    let service = this.subject();
    expect(service.get('baseLayer')).to.equal('OpenStreetMap');
    expect(service.get('overlayLayers')).to.deep.equal(['Airspace']);
  });

  it('reads layers from cookies', function() {
    let service = this.subject();
    expect(service.get('baseLayer')).to.equal('Foo');
    expect(service.get('overlayLayers')).to.deep.equal(['Bar', 'Baz']);
  });

  it('handles empty overlays cookie correctly', function() {
    this.register('service:cookies', Service.extend({
      read(key) {
        if (key === OVERLAY_LAYERS_COOKIE_KEY) {
          return '';
        }
      },
    }));

    let service = this.subject();
    expect(service.get('overlayLayers')).to.deep.equal([]);
  });

  it('prioritizes layers from query params', function() {
    let router = this.container.lookup('service:router');

    router.set('currentURL', '/flights/17537?baselayer=alternate&overlays=foo;bar');

    let service = this.subject();
    expect(service.get('baseLayer')).to.equal('alternate');
    expect(service.get('overlayLayers')).to.deep.equal(['foo', 'bar']);

    router.set('currentURL', '/flights/17537');

    expect(service.get('baseLayer')).to.equal('Foo');
    expect(service.get('overlayLayers')).to.deep.equal(['Bar', 'Baz']);
  });

  it('handles empty overlays query param correctly', function() {
    let router = this.container.lookup('service:router');
    router.set('currentURL', '/flights/17537?baselayer=alternate&overlays=');

    let service = this.subject();
    expect(service.get('overlayLayers')).to.deep.equal([]);
  });
});
