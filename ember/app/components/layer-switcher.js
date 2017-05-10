import Ember from 'ember';
import $ from 'jquery';

export default Ember.Component.extend({
  cookies: Ember.inject.service(),

  classNames: ['GraphicLayerSwitcher', 'ol-unselectable'],

  map: null,
  open: false,
  baseLayers: null,
  overlayLayers: null,

  didInsertElement() {
    let mouseHandler = event => {
      if (this.$().find(event.target).length === 0) {
        this.set('open', false);
      }
    };

    this.set('mouseHandler', mouseHandler);
    $(document).on('mouseup touchend', mouseHandler);
  },

  willDestroyElement() {
    let mouseHandler = this.get('mouseHandler');
    $(document).off('mouseup touchend', mouseHandler);
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
          .forEach(it => it.setVisible(!it.getVisible()));
      }

      this.setLayerCookies();
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

  setLayerCookies() {
    let cookies = this.get('cookies');
    let layers = this.get('map').getLayers().getArray();

    let baseLayer = layers.filter(it => (it.get('base_layer') && it.getVisible()))[0];
    cookies.write('base_layer', baseLayer.get('name'), { path: '/', expires: new Date('2099-12-31') });

    let overlayLayers = layers.filter(it => (!it.get('base_layer') && it.getVisible()))
      .map(it => it.get('name'))
      .join(';');

    cookies.write('overlay_layers', overlayLayers, { path: '/', expires: new Date('2099-12-31') });
  },
});
