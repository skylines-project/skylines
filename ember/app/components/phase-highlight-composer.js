import Ember from 'ember';
import ol from 'openlayers';

import computedPoint from '../computed/computed-point';

export default Ember.Component.extend({
  tagName: '',

  map: null,
  paddingFn: null,
  coordinates: null,

  startCoordinate: Ember.computed.readOnly('coordinates.firstObject'),
  endCoordinate: Ember.computed.readOnly('coordinates.lastObject'),

  startPoint: computedPoint('coordinates.firstObject'),
  endPoint: computedPoint('coordinates.lastObject'),

  coordinatesObserver: Ember.observer('coordinates.[]', function() {
    this.adjustMapView();
    Ember.run.once(this.get('map'), 'render');
  }),

  init() {
    this._super(...arguments);

    let startIcon = new ol.style.Icon({
      anchor: [0.5, 1],
      src: '/images/marker-green.png',
    });
    startIcon.load();

    let endIcon = new ol.style.Icon({
      anchor: [0.5, 1],
      src: '/images/marker.png',
    });
    endIcon.load();

    let startStyle = new ol.style.Style({ image: startIcon });
    this.set('startStyle', startStyle);

    let endStyle = new ol.style.Style({ image: endIcon });
    this.set('endStyle', endStyle);

    // activate coordinatesObserver
    this.get('coordinates');
  },

  didInsertElement() {
    this.get('map').on('postcompose', this.onPostCompose, this);
  },

  willDestroyElement() {
    this.get('map').un('postcompose', this.onPostCompose, this);
  },

  onPostCompose(e) {
    this.renderMarkers(e.vectorContext);
  },

  renderMarkers(context) {
    this.renderMarker(context, this.get('startStyle'), this.get('startPoint'));
    this.renderMarker(context, this.get('endStyle'), this.get('endPoint'));
  },

  renderMarker(context, style, coordinate) {
    if (coordinate) {
      context.setStyle(style);
      context.drawGeometry(coordinate);
    }
  },

  adjustMapView() {
    let coordinates = this.get('coordinates');
    if (coordinates) {
      let map = this.get('map');
      let extent = ol.extent.boundingExtent(coordinates);
      let padding = this.getWithDefault('calculatePadding', Ember.K)();
      map.getView().fit(extent, map.getSize(), { padding });
    }
  },
});
