import Ember from 'ember';
import ol from 'openlayers';

export default Ember.Component.extend({
  tagName: '',

  map: null,
  fixes: null,

  fixesObserver: Ember.observer('fixes.@each.pointXY', function() {
    Ember.run.once(this.get('map'), 'render');
  }),

  init() {
    this._super(...arguments);

    let icon = new ol.style.Icon({
      anchor: [0.5, 0.5],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      size: [40, 24],
      src: '/images/glider_symbol.png',
      rotation: 0,
      rotateWithView: true,
    });

    icon.load();

    this.set('icon', icon);

    let style = new ol.style.Style({ image: icon });
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
    let icon = this.get('icon');
    let style = this.get('style');

    this.get('fixes').forEach(fix => {
      let point = fix.get('pointXY');
      if (point) {
        icon.setRotation(fix.get('heading'));
        context.setStyle(style);
        context.drawGeometry(point);
      }
    });
  },
});
