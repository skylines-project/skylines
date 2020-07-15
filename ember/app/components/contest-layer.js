import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

const DEFAULT_COLOR = '#004bbd';

export default class ContestLayer extends Component {
  tagName = '';

  map = null;
  flights = null;

  @computed('flights.@each.contests')
  get contests() {
    return this.flights.map(flight => flight.get('contests')).reduce((a, b) => a.concat(b), []);
  }

  @computed
  get layer() {
    return new ol.layer.Vector({
      source: new ol.source.Vector(),
      style: style_function,
      name: 'Contest',
      zIndex: 49,
    });
  }

  @computed('layer')
  get source() {
    return this.layer.getSource();
  }

  @computed
  get visible() {
    return this.layer.getVisible();
  }

  set visible(value) {
    this.layer.setVisible(value);
  }

  didInsertElement() {
    super.didInsertElement(...arguments);
    this.map.addLayer(this.layer);
  }

  willDestroyElement() {
    super.willDestroyElement(...arguments);
    this.map.removeLayer(this.layer);
  }
}

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
