import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

const DEFAULT_COLOR = '#004bbd';

export default Component.extend({
  tagName: '',

  map: null,
  flights: null,

  layer: computed(function() {
    return new ol.layer.Vector({
      source: new ol.source.Vector(),
      style: style_function,
      name: 'Flight',
      zIndex: 50,
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

/**
 * Determin the drawing style for the feature
 * @param {ol.feature} feature Feature to style
 * @return {!Array<ol.style.Style>} Style of the feature
 */
function style_function(feature) {
  let color = DEFAULT_COLOR;
  if (feature.getKeys().includes('color')) {
    color = feature.get('color');
  }

  return [
    new ol.style.Style({
      stroke: new ol.style.Stroke({ color, width: 2 }),
      zIndex: 1000,
    }),
  ];
}
