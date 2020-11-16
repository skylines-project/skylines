import Component from '@ember/component';
import { observer } from '@ember/object';
import { once, next } from '@ember/runloop';
import { inject as service } from '@ember/service';

import config from '../config/environment';

export default Component.extend({
  tagName: '',

  mapSettings: service(),

  mapSettingsObserver: observer('mapSettings.baseLayer', 'mapSettings.overlayLayers.[]', function () {
    once(this, 'updateLayerVisibilities');
  }),

  mapBoxUrl: config.MAPBOX_TILE_URL,
  bingApiKey: config.BING_API_KEY,

  init() {
    this._super(...arguments);

    next(() => this.updateLayerVisibilities());
  },

  updateLayerVisibilities() {
    let mapSettings = this.mapSettings;
    let baseLayerNames = mapSettings.get('baseLayer');
    let overlayLayerNames = mapSettings.get('overlayLayers');

    let layers = this.map
      .getLayers()
      .getArray()
      .filter(layer => layer.get('display_in_layer_switcher'));

    let baseLayers = layers.filter(layer => layer.get('base_layer'));
    baseLayers.forEach(layer => {
      layer.setVisible(layer.get('name') === baseLayerNames);
    });

    if (!baseLayers.find(layer => layer.get('name') === baseLayerNames)) {
      baseLayers.find(layer => layer.get('name') === 'OpenStreetMap').setVisible(true);
    }

    let overlayLayers = layers.filter(layer => !layer.get('base_layer'));
    overlayLayers.forEach(layer => {
      layer.setVisible(overlayLayerNames.includes(layer.get('name')));
    });
  },
});
