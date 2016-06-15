import Ember from 'ember';

export default Ember.Component.extend({
  classNames: ['GraphicLayerSwitcher', 'ol-unselectable'],

  map: null,
  open: false,
  baseLayers: [],
  overlayLayers: [],

  didInsertElement() {
    Ember.$(document).on('mouseup touchend', e => {
      if (this.$().find(e.target).length === 0) {
        this.set('open', false);
      }
    });
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

  setLayerCookies() {
    let layers = this.get('map').getLayers().getArray();

    let baseLayer = layers.filter(it => (it.get('base_layer') && it.getVisible()))[0];
    Ember.$.cookie('base_layer', baseLayer.get('name'), { path: '/', expires: 365 });

    let overlayLayers = layers.filter(it => (!it.get('base_layer') && it.getVisible()))
      .map(it => it.get('name'))
      .join(';');

    Ember.$.cookie('overlay_layers', overlayLayers, { path: '/', expires: 365 });
  },

  actions: {
    open() {
      this.updateLayers();
      this.set('open', true);
    },

    select(layer) {
      if (layer.isBaseLayer) {
        this.get('map').getLayers().getArray()
          .filter(it => it.get('base_layer'))
          .forEach(it => it.setVisible(it.get('id') === layer.id));

      } else {
        this.get('map').getLayers().getArray()
          .filter(it => (it.get('id') === layer.id))
          .forEach(it => it.setVisible(!it.getVisible()))
      }

      this.setLayerCookies();
      this.updateLayers();
    },
  },
});
