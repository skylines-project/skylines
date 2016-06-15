import Ember from 'ember';
import ol from 'openlayers';

export default Ember.Component.extend({
  tagName: '',

  source: null,
  location: null,

  feature: Ember.computed(function() {
    let location = this.get('location');
    let transformed = ol.proj.transform(location, 'EPSG:4326', 'EPSG:3857');

    return new ol.Feature({
      geometry: new ol.geom.Point(transformed),
    });
  }),

  didInsertElement() {
    this.get('source').addFeature(this.get('feature'));
  },

  willDestroyElement() {
    this.get('source').removeFeature(this.get('feature'));
  },
});
