import Component from '@glimmer/component';

import Feature from 'ol/Feature';

export default class ContestLayerFeature extends Component {
  constructor() {
    super(...arguments);

    const { contest, source } = this.args;

    let { geometry, isTriangle } = contest;
    this.feature = new Feature({ geometry, isTriangle });

    source.addFeature(this.feature);
  }

  willDestroy() {
    super.willDestroy(...arguments);
    this.args.source.removeFeature(this.feature);
  }
}
