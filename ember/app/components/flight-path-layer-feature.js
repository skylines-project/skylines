import Component from '@glimmer/component';

import ol from 'openlayers';

export default class FlightPathLayerFeature extends Component {
  feature = new ol.Feature({
    geometry: this.args.flight.get('geometry'),
    sfid: this.args.flight.get('id'),
    color: this.args.flight.get('color'),
    type: 'flight',
  });

  constructor() {
    super(...arguments);
    this.args.source.addFeature(this.feature);
  }

  willDestroy() {
    super.willDestroy(...arguments);
    this.args.source.removeFeature(this.feature);
  }
}
