import { computed } from '@ember/object';
import Component from '@glimmer/component';

import Feature from 'ol/Feature';

export default class ContestLayerFeature extends Component {
  @computed
  get feature() {
    let contest = this.args.contest;
    return new Feature({
      geometry: contest.geometry,
      sfid: contest.flightId,
      color: contest.color,
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
