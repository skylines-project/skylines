import { inject as service } from '@ember/service';
import Component from '@ember/component';
import $ from 'jquery';

export default Component.extend({
  mapSettings: service(),

  classNames: ['GraphicLayerSwitcher', 'ol-unselectable'],

  map: null,
  open: false,
  baseLayers: null,
  overlayLayers: null,

  didInsertElement() {
    this._super(...arguments);
    let mouseHandler = event => {
      if (this.$().find(event.target).length === 0) {
        this.set('open', false);
      }
    };

    this.set('mouseHandler', mouseHandler);
    $(document).on('mouseup touchend', mouseHandler);
  },

  willDestroyElement() {
    this._super(...arguments);
    let mouseHandler = this.get('mouseHandler');
    $(document).off('mouseup touchend', mouseHandler);
  },

  actions: {
    open() {
      this.updateLayers();
      this.set('open', true);
    },

    select(layer) {
      let mapSettings = this.get('mapSettings');

      if (layer.isBaseLayer) {
        mapSettings.setBaseLayer(layer.name);

        this.get('map').getLayers().getArray()
          .filter(it => it.get('base_layer'))
          .forEach(it => it.setVisible(it.get('id') === layer.id));

      } else {
        mapSettings.toggleOverlayLayer(layer.name);

        this.get('map').getLayers().getArray()
          .filter(it => (it.get('id') === layer.id))
          .forEach(it => it.setVisible(!it.getVisible()));
      }

      this.updateLayers();
    },
  },

  updateLayers() {
    let layers = this.get('map').getLayers().getArray()
      .filter(layer => layer.get('display_in_layer_switcher'))
      .map(layer => {
        let id = layer.get('id');
        let name = layer.get('name');
        let visible = layer.getVisible();
        let isBaseLayer = layer.get('base_layer');
        return { id, name, visible, isBaseLayer };
      });

    this.set('baseLayers', layers.filter(layer => layer.isBaseLayer));
    this.set('overlayLayers', layers.filter(layer => !layer.isBaseLayer));
  },
});
