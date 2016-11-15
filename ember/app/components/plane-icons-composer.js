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

    let glider = new ol.style.Icon({
      anchor: [0.5, 0.5],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      size: [40, 24],
      src: '/images/glider_symbol.png',
      rotation: 0,
      rotateWithView: true,
    });
    let motorglider = new ol.style.Icon({
      anchor: [0.5, 0.5],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      size: [40, 24],
      src: '/images/motorglider_symbol.png',
      rotation: 0,
      rotateWithView: true,
    });
    let paraglider = new ol.style.Icon({
      anchor: [0.5, 0.5],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      size: [40, 24],
      src: '/images/paraglider_symbol.png',
      rotation: 0,
      rotateWithView: true,
    });
    let hangglider = new ol.style.Icon({
      anchor: [0.5, 0.5],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      size: [40, 14],
      src: '/images/hangglider_symbol.png',
      rotation: 0,
      rotateWithView: true,
    });
    // TODO: draw the symbol and update src property
    let ul = new ol.style.Icon({
      anchor: [0.5, 0.5],
      anchorXUnits: 'fraction',
      anchorYUnits: 'fraction',
      size: [24, 24],
      src: '/images/logo.png',
      rotation: 0,
      rotateWithView: true,
    });

    let styles = { glider, motorglider, paraglider, hangglider, ul };
    // TODO: use a loop to load the styles
    styles.glider.load();
    styles.motorglider.load();
    styles.paraglider.load();
    styles.hangglider.load();
    styles.ul.load();

    this.set('styles', styles);
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
    let styles = this.get('styles');

    this.get('fixes').forEach(fix => {
      let point = fix.get('pointXY');

      if (point) {
        let type = fix.flight.model && fix.flight.model.type || 'glider';
        let style = styles[type];

        style.setRotation(fix.get('heading'));
        context.setImageStyle(style);
        context.drawPointGeometry(point);
      }
    });
  },
});
