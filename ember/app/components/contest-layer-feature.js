import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

export default class ContestLayerFeature extends Component {
  tagName = '';

  @computed
  get feature() {
    let contest = this.contest;
    return new ol.Feature({
      geometry: contest.get('geometry'),
      sfid: contest.get('flightId'),
      color: contest.get('color'),
      type: 'contest',
    });
  }

  init() {
    super.init(...arguments);
    this.source.addFeature(this.feature);
  }

  willDestroy() {
    super.willDestroy(...arguments);
    this.source.removeFeature(this.feature);
  }
}
