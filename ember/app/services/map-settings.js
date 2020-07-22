import { action, computed } from '@ember/object';
import { or } from '@ember/object/computed';
import Service, { inject as service } from '@ember/service';
import { tracked } from '@glimmer/tracking';

import parseQueryString from 'skylines/utils/parse-query-string';

export const BASE_LAYER_COOKIE_KEY = 'base_layer';
export const OVERLAY_LAYERS_COOKIE_KEY = 'overlay_layers';

export default class MapSettingsService extends Service {
  @service cookies;
  @service router;

  @tracked _baseLayer = 'OpenStreetMap';
  @tracked _overlayLayers = ['Airspace'];

  @or('_query.baselayer', '_baseLayer') baseLayer;

  @computed('_query.overlays', '_overlayLayers')
  get overlayLayers() {
    let queryOverlays = this.get('_query.overlays');
    if (queryOverlays === undefined) {
      return this._overlayLayers;
    } else if (queryOverlays === '') {
      return [];
    } else {
      return queryOverlays.split(';');
    }
  }

  @computed('router.currentURL')
  get _query() {
    let currentURL = this.get('router.currentURL');
    let queryString = extractQueryString(currentURL);
    return parseQueryString(queryString);
  }

  constructor() {
    super(...arguments);

    let cookies = this.cookies;
    let cookieBaseLayer = cookies.read(BASE_LAYER_COOKIE_KEY);
    if (cookieBaseLayer) {
      this._baseLayer = cookieBaseLayer;
    }

    let cookieOverlayLayers = cookies.read(OVERLAY_LAYERS_COOKIE_KEY);
    if (cookieOverlayLayers !== undefined) {
      this._overlayLayers = cookieOverlayLayers === '' ? [] : cookieOverlayLayers.split(';');
    }
  }

  isLayerVisible(layer) {
    return this.baseLayer === layer || this.overlayLayers.includes(layer);
  }

  @action setBaseLayer(baseLayer) {
    this._baseLayer = baseLayer;
    this.cookies.write(BASE_LAYER_COOKIE_KEY, baseLayer, { path: '/', expires: new Date('2099-12-31') });
  }

  @action toggleOverlayLayer(overlayLayer) {
    let overlayLayers = this.overlayLayers;
    if (overlayLayers.includes(overlayLayer)) {
      overlayLayers.removeObject(overlayLayer);
    } else {
      overlayLayers.pushObject(overlayLayer);
    }

    this.cookies.write(OVERLAY_LAYERS_COOKIE_KEY, overlayLayers.join(';'), {
      path: '/',
      expires: new Date('2099-12-31'),
    });
  }
}

function extractQueryString(url) {
  let qIndex = url.indexOf('?');
  if (qIndex === -1) {
    return null;
  }

  return url.slice(qIndex + 1);
}
