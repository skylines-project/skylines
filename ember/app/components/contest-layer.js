import Component from '@ember/component';
import { action, computed } from '@ember/object';

import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Stroke from 'ol/style/Stroke';
import Style from 'ol/style/Style';

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
    new Style({
      stroke: new Stroke({ color, width: 2, lineDash: [5] }),
      zIndex: 999,
    }),
  ];
}
