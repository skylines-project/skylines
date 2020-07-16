import Component from '@ember/component';
import { action } from '@ember/object';
import { htmlSafe } from '@ember/template';

import ol from 'openlayers';

export default class PlaneLabelOverlay extends Component {
  tagName = '';

  map = null;
  flight = null;
  position = null;
  overlay = null;

  get style() {
    return htmlSafe(`background: ${this.flight.color}`);
  }

  @action
  addToMap(element) {
    let { position } = this;

    let { offsetWidth } = element;
    let offset = [-offsetWidth / 2, -40];

    this.overlay = new ol.Overlay({ element, offset, position });
    this.map.addOverlay(this.overlay);
  }

  @action
  updatePosition() {
    this.overlay.setPosition(this.position);
  }

  willDestroy() {
    super.willDestroy(...arguments);
    this.map.removeOverlay(this.overlay);
  }
}
