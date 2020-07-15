import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

export default class TakeoffsLayerFeature extends Component {
  tagName = '';

  source = null;
  location = null;

  @computed
  get feature() {
    let location = this.location;
    let transformed = ol.proj.transform(location, 'EPSG:4326', 'EPSG:3857');

    return new ol.Feature({
      geometry: new ol.geom.Point(transformed),
    });
  }

  didInsertElement() {
    super.didInsertElement(...arguments);
    this.source.addFeature(this.feature);
  }

  willDestroyElement() {
    super.willDestroyElement(...arguments);
    this.source.removeFeature(this.feature);
  }
}
