import Component from '@ember/component';
import { inject as service } from '@ember/service';

export default Component.extend({
  tagName: '',

  mapSettings: service(),

  map: null,
  open: false,
  baseLayers: null,
  overlayLayers: null,

  actions: {
    open() {
      this.updateLayers();
      this.set('open', true);
    },

    select(layer) {
      let mapSettings = this.mapSettings;

      if (layer.isBaseLayer) {
        mapSettings.setBaseLayer(layer.name);
      } else {
        mapSettings.toggleOverlayLayer(layer.name);
      }

      this.updateLayers();
    },
  },

  updateLayers() {
    let mapSettings = this.mapSettings;

    let layers = this.map
      .getLayers()
      .getArray()
      .filter(layer => layer.get('display_in_layer_switcher'))
      .map(layer => {
        let id = layer.get('id');
        let name = layer.get('name');
        let visible = mapSettings.isLayerVisible(name);
        let isBaseLayer = layer.get('base_layer');
        return { id, name, visible, isBaseLayer };
      });

    this.set('baseLayers', layers.filter(layer => layer.isBaseLayer));
    this.set('overlayLayers', layers.filter(layer => !layer.isBaseLayer));
  },
});
