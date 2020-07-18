import Component from '@glimmer/component';

import ol from 'openlayers';

const DEFAULT_COLOR = '#004bbd';

export default class FlightPathLayer extends Component {
  layer = new ol.layer.Vector({
    source: new ol.source.Vector(),
    style: style_function,
    name: 'Flight',
    zIndex: 50,
  });

  get source() {
    return this.layer.getSource();
  }

  constructor() {
    super(...arguments);
    this.args.map.addLayer(this.layer);
  }

  willDestroy() {
    super.willDestroy(...arguments);
    this.args.map.removeLayer(this.layer);
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
      stroke: new ol.style.Stroke({ color, width: 2 }),
      zIndex: 1000,
    }),
  ];
}
