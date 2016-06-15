/* globals ol */

import Ember from 'ember';

export default Ember.Component.extend({
  fixCalc: Ember.inject.service(),

  tagName: '',

  map: null,

  fixes: Ember.computed.readOnly('fixCalc.fixes'),
  fixesObserver: Ember.observer('fixes.@each.point', function() {
    Ember.run.once(this.get('map'), 'render');
  }),

  init() {
    this._super(...arguments);

    let style = new ol.style.Icon({
      anchor: [0.5, 0.5],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      size: [40, 24],
      src: '/images/glider_symbol.png',
      rotation: 0,
      rotateWithView: true
    });

    style.load();

    this.set('style', style);
  },

  didInsertElement() {
    this.get('map').on('postcompose', this.onPostCompose, this);
  },

  willDestroyElement() {
    this.get('map').un('postcompose', this.onPostCompose, this);
  },

  onPostCompose(e) {
    this.renderIcons(e.vectorContext);
  },

  renderIcons(context) {
    let style = this.get('style');

    this.get('fixes').forEach(fix => {
      if (fix.get('point')) {
        style.setRotation(fix.get('heading'));
        context.setImageStyle(style);
        context.drawPointGeometry(fix.get('point'));
      }
    });
  },
});
