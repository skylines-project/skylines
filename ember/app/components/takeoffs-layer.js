import Ember from 'ember';
import ol from 'openlayers';

export default Ember.Component.extend({
  tagName: '',

  map: null,
  locations: null,

  layer: Ember.computed(function() {
    return new ol.layer.Vector({
      source: new ol.source.Vector(),
      style: new ol.style.Style({
        image: new ol.style.Icon(({
          anchor: [0.5, 1],
          src: '/images/marker-gold.png',
        })),
      }),
      name: 'Takeoff Locations',
      id: 'TakeoffLocations',
      zIndex: 51,
    });
  }),

  source: Ember.computed('layer', function() {
    return this.get('layer').getSource();
  }),

  didInsertElement() {
    this.get('map').addLayer(this.get('layer'));
  },

  willDestroyElement() {
    this.get('map').removeLayer(this.get('layer'));
  },
});
