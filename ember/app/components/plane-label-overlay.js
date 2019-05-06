import Component from '@ember/component';

import $ from 'jquery';
import ol from 'openlayers';

export default Component.extend({
  tagName: '',

  map: null,
  flight: null,
  position: null,

  overlay: null,

  init() {
    this._super(...arguments);

    let badgeStyle = `display: inline-block; text-align: center; background: ${this.get('flight.color')}`;

    let id = this.getWithDefault('flight.competition_id', '') || this.getWithDefault('flight.registration', '');
    let badge = $(`<span class="badge plane_marker" style="${badgeStyle}">
      ${id}
    </span>`);

    this.set(
      'overlay',
      new ol.Overlay({
        element: badge.get(0),
      }),
    );
  },

  didReceiveAttrs() {
    this._super(...arguments);
    this.overlay.setPosition(this.position);
  },

  didInsertElement() {
    this._super(...arguments);
    let overlay = this.overlay;
    this.map.addOverlay(overlay);

    let width = $(overlay.getElement()).width();
    overlay.setOffset([-width / 2, -40]);
  },

  willDestroyElement() {
    this._super(...arguments);
    let overlay = this.overlay;
    this.map.removeOverlay(overlay);
  },
});
