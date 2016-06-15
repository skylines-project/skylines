/* globals ol */

import Ember from 'ember';

export default Ember.Component.extend({
  tagName: '',

  map: null,
  flights: null,

  layer: Ember.computed(function() {
    return new ol.layer.Vector({
      source: new ol.source.Vector(),
      style: style_function,
      name: 'Flight',
      zIndex: 50,
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

/**
 * Determin the drawing style for the feature
 * @param {ol.feature} feature Feature to style
 * @return {!Array<ol.style.Style>} Style of the feature
 */
function style_function(feature) {
  var color = '#004bbd'; // default color
  if (feature.getKeys().contains('color')) {
    color = feature.get('color');
  }

  return [new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: color,
      width: 2,
    }),
    zIndex: 1000,
  })];
}
