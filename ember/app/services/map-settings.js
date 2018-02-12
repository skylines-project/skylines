import Service, { inject as service } from '@ember/service';
import { computed } from '@ember/object';

import { or } from 'ember-awesome-macros';

import parseQueryString from 'skylines/utils/parse-query-string';

export const BASE_LAYER_COOKIE_KEY = 'base_layer';
export const OVERLAY_LAYERS_COOKIE_KEY = 'overlay_layers';

export default Service.extend({
  cookies: service(),
  router: service(),

  _baseLayer: 'OpenStreetMap',
  // _overlayLayers: ['Airspace'],

  baseLayer: or('_query.baselayer', '_baseLayer'),
  overlayLayers: computed('_query.overlays', '_overlayLayers', function() {
    let queryOverlays = this.get('_query.overlays');
    if (queryOverlays === undefined) {
      return this.get('_overlayLayers');
    } else if (queryOverlays === '') {
      return [];
    } else {
      return queryOverlays.split(';');
    }
  }),

  _query: computed('router.currentURL', function() {
    let currentURL = this.get('router.currentURL');
    let queryString = extractQueryString(currentURL);
    return parseQueryString(queryString);
  }),

  init() {
    this._super(...arguments);
    this.set('_overlayLayers', ['Airspace']);

    let cookies = this.get('cookies');
    let cookieBaseLayer = cookies.read(BASE_LAYER_COOKIE_KEY);
    if (cookieBaseLayer) {
      this.set('_baseLayer', cookieBaseLayer);
    }

    let cookieOverlayLayers = cookies.read(OVERLAY_LAYERS_COOKIE_KEY);
    if (cookieOverlayLayers !== undefined) {
      this.set('_overlayLayers', cookieOverlayLayers === '' ? [] : cookieOverlayLayers.split(';'));
    }
  },

  isLayerVisible(layer) {
    return this.get('baseLayer') === layer || this.get('overlayLayers').includes(layer);
  },

  setBaseLayer(baseLayer) {
    this.set('_baseLayer', baseLayer);
    this.get('cookies').write(BASE_LAYER_COOKIE_KEY, baseLayer, { path: '/', expires: new Date('2099-12-31') });
  },

  toggleOverlayLayer(overlayLayer) {
    let overlayLayers = this.get('overlayLayers');
    if (overlayLayers.includes(overlayLayer)) {
      overlayLayers.removeObject(overlayLayer);
    } else {
      overlayLayers.pushObject(overlayLayer);
    }

    this.get('cookies').write(OVERLAY_LAYERS_COOKIE_KEY, overlayLayers.join(';'), { path: '/', expires: new Date('2099-12-31') });
  },
});

function extractQueryString(url) {
  let qIndex = url.indexOf('?');
  if (qIndex === -1) {
    return null;
  }

  return url.slice(qIndex + 1);
}
