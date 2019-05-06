import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

export default Component.extend({
  tagName: '',

  map: null,
  locations: null,

  layer: computed(function() {
    return new ol.layer.Vector({
      source: new ol.source.Vector(),
      style: new ol.style.Style({
        image: new ol.style.Icon({
          anchor: [0.5, 1],
          src: '/images/marker-gold.png',
        }),
      }),
      name: 'Takeoff Locations',
      id: 'TakeoffLocations',
      zIndex: 51,
    });
  }),

  source: computed('layer', function() {
    return this.layer.getSource();
  }),

  didInsertElement() {
    this._super(...arguments);
    this.map.addLayer(this.layer);
  },

  willDestroyElement() {
    this._super(...arguments);
    this.map.removeLayer(this.layer);
  },
});
