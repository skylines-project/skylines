import { computed } from '@ember/object';

import Component from '@glimmer/component';
import ol from 'openlayers';

export default class ContestLayerFeature extends Component {
  @computed
  get feature() {
    let contest = this.args.contest;
    return new ol.Feature({
      geometry: contest.get('geometry'),
      sfid: contest.get('flightId'),
      color: contest.get('color'),
      type: 'contest',
    });
  }

  constructor() {
    super(...arguments);
    this.args.source.addFeature(this.feature);
  }

  willDestroy() {
    super.willDestroy(...arguments);
    this.args.source.removeFeature(this.feature);
  }
}
