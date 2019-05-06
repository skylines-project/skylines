import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

const DEFAULT_COLOR = '#004bbd';

export default Component.extend({
  tagName: '',

  map: null,
  flights: null,

  contests: computed('flights.@each.contests', function() {
    return this.flights.map(flight => flight.get('contests')).reduce((a, b) => a.concat(b), []);
  }),

  layer: computed(function() {
    return new ol.layer.Vector({
      source: new ol.source.Vector(),
      style: style_function,
      name: 'Contest',
      zIndex: 49,
    });
  }),

  source: computed('layer', function() {
    return this.layer.getSource();
  }),

  visible: computed({
    get() {
      return this.layer.getVisible();
    },
    set(key, value) {
      this.layer.setVisible(value);
    },
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
      stroke: new ol.style.Stroke({ color, width: 2, lineDash: [5] }),
      zIndex: 999,
    }),
  ];
}
