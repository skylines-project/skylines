import Component from '@glimmer/component';

import Feature from 'ol/Feature';

export default class FlightPathLayerFeature extends Component {
  feature = new Feature({
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
