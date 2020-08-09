import { action, computed } from '@ember/object';
import Component from '@glimmer/component';

import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Stroke from 'ol/style/Stroke';
import Style from 'ol/style/Style';

const DEFAULT_COLOR = '#004bbd';

export default class ContestLayer extends Component {
  @computed('args.flights.@each.contests')
  get contests() {
    return this.args.flights.map(flight => flight.get('contests')).reduce((a, b) => a.concat(b), []);
  }

  @computed
  get layer() {
    return new VectorLayer({
      source: new VectorSource(),
      style: style_function,
      name: 'Contest',
      zIndex: 49,
    });
  }

  @computed('layer')
  get source() {
    return this.layer.getSource();
  }

  @action
  setVisible([value]) {
    this.layer.setVisible(value);
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
      stroke: new Stroke({ color, width: 2, lineDash: [5] }),
      zIndex: 999,
    }),
  ];
}
