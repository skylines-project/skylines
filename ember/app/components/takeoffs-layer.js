import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

export default class TakeoffsLayer extends Component {
  tagName = '';

  map = null;
  locations = null;

  @computed
  get layer() {
    return new ol.layer.Vector({
      source: new ol.source.Vector(),
      style: new ol.style.Style({
        image: new ol.style.Icon({
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
