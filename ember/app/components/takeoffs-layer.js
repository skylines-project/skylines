import Component from '@ember/component';
import { computed } from '@ember/object';

import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Icon from 'ol/style/Icon';
import Style from 'ol/style/Style';

export default class TakeoffsLayer extends Component {
  tagName = '';

  map = null;
  locations = null;

  @computed
  get layer() {
    return new VectorLayer({
      source: new VectorSource(),
      style: new Style({
        image: new Icon({
          anchor: [0.5, 1],
          src: '/images/marker-gold.png',
        }),
      }),
      name: 'Takeoff Locations',
      id: 'TakeoffLocations',
      zIndex: 51,
    });
  }

  @computed('layer')
  get source() {
    return this.layer.getSource();
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
