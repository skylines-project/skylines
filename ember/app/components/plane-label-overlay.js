import { action } from '@ember/object';
import { htmlSafe } from '@ember/template';
import Component from '@glimmer/component';

import Overlay from 'ol/Overlay';

export default class PlaneLabelOverlay extends Component {
  get style() {
    return htmlSafe(`background: ${this.args.flight.color}`);
  }

  @action
  addToMap(element) {
    let { position } = this.args;

    let { offsetWidth } = element;
    let offset = [-offsetWidth / 2, -40];

    this.overlay = new Overlay({ element, offset });
    this.args.map.addOverlay(this.overlay);

    // see https://github.com/openlayers/ol-cesium/issues/679
    this.overlay.setPosition(position);
  }

  @action
  updatePosition() {
    this.overlay.setPosition(this.args.position);
  }

  willDestroy() {
    this.args.map.removeOverlay(this.overlay);
  }
}
