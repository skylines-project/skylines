import Ember from 'ember';
import ol from 'openlayers';

export default Ember.Component.extend({
  tagName: '',

  map: null,
  flight: null,
  position: null,

  overlay: null,

  init() {
    this._super(...arguments);

    let badgeStyle = `display: inline-block; text-align: center; background: ${this.get('flight.color')}`;

    let badge = Ember.$(`<span class="badge plane_marker" style="${badgeStyle}">
      ${this.getWithDefault('flight.competition_id', '')}
    </span>`);

    this.set('overlay', new ol.Overlay({
      element: badge.get(0),
    }));
  },

  didReceiveAttrs() {
    this.get('overlay').setPosition(this.get('position'));
  },

  didInsertElement() {
    let overlay = this.get('overlay');
    this.get('map').addOverlay(overlay);

    let width = Ember.$(overlay.getElement()).width();
    overlay.setOffset([-width / 2, -40]);
  },

  willDestroyElement() {
    let overlay = this.get('overlay');
    this.get('map').removeOverlay(overlay);
  },
});
