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
  },

  updateLayers() {
    let layers = this.map
      .getLayers()
      .getArray()
      .filter(layer => layer.get('display_in_layer_switcher'))
      .map(layer => {
        let name = layer.get('name');
        let isBaseLayer = layer.get('base_layer');
        return { name, isBaseLayer };
      });

    this.set(
      'baseLayers',
      layers.filter(layer => layer.isBaseLayer).map(it => it.name),
    );
    this.set(
      'overlayLayers',
      layers.filter(layer => !layer.isBaseLayer).map(it => it.name),
    );
  },
});
