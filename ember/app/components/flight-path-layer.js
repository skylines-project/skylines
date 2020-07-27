import Component from '@glimmer/component';

import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Stroke from 'ol/style/Stroke';
import Style from 'ol/style/Style';

const DEFAULT_COLOR = '#004bbd';

export default class FlightPathLayer extends Component {
  layer = new VectorLayer({
    source: new VectorSource(),
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
    new Style({
      stroke: new Stroke({ color, width: 2 }),
      zIndex: 1000,
    }),
  ];
}
