/* globals ol */

import Ember from 'ember';

export default Ember.Component.extend({
  flightPhase: Ember.inject.service(),

  tagName: '',

  map: null,
  paddingFn: null,

  coordinates: Ember.computed.readOnly('flightPhase.coordinates'),
  startPoint: Ember.computed.readOnly('flightPhase.startPoint'),
  endPoint: Ember.computed.readOnly('flightPhase.endPoint'),

  coordinatesObserver: Ember.observer('coordinates.[]', function() {
    this.adjustMapView();
    this.get('map').render();
  }),

  init() {
    this._super(...arguments);

    let startStyle = new ol.style.Icon({
      anchor: [0.5, 1],
      src: '/vendor/openlayers/img/marker-green.png'
    });
    let endStyle = new ol.style.Icon({
      anchor: [0.5, 1],
      src: '/vendor/openlayers/img/marker.png'
    });

    startStyle.load();
    endStyle.load();

    this.set('startStyle', startStyle);
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
      context.setImageStyle(style);
      context.drawPointGeometry(coordinate);
    }
  },

  adjustMapView() {
    let coordinates = this.get('coordinates');
    if (coordinates) {
      let map = this.get('map');
      let extent = ol.extent.boundingExtent(coordinates);
      let padding = window.paddingFn();
      map.getView().fit(extent, map.getSize(), { padding });
    }
  }
});
