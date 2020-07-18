import { action } from '@ember/object';
import { htmlSafe } from '@ember/template';
import Component from '@glimmer/component';

import ol from 'openlayers';

export default class PlaneLabelOverlay extends Component {
  get style() {
    return htmlSafe(`background: ${this.args.flight.color}`);
  }

  @action
  addToMap(element) {
    let { position } = this.args;

    let { offsetWidth } = element;
    let offset = [-offsetWidth / 2, -40];

    this.overlay = new ol.Overlay({ element, offset, position });
    this.args.map.addOverlay(this.overlay);
  }

  @action
  updatePosition() {
    this.overlay.setPosition(this.args.position);
  }

  willDestroy() {
    this.args.map.removeOverlay(this.overlay);
  }
}
