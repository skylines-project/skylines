import Component from '@ember/component';
import { computed } from '@ember/object';

import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import { transform } from 'ol/proj';

export default class TakeoffsLayerFeature extends Component {
  tagName = '';

  source = null;
  location = null;

  @computed
  get feature() {
    let location = this.location;
    let transformed = transform(location, 'EPSG:4326', 'EPSG:3857');

    return new Feature({
      geometry: new Point(transformed),
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
