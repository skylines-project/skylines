import Component from '@ember/component';
import { action, observer } from '@ember/object';
import { readOnly } from '@ember/object/computed';
import { once } from '@ember/runloop';

import { boundingExtent } from 'ol/extent';
import Icon from 'ol/style/Icon';
import Style from 'ol/style/Style';

import computedPoint from '../computed/computed-point';

export default Component.extend({
  tagName: '',

  map: null,
  paddingFn: null,
  coordinates: null,
  calculatePadding() {},

  startCoordinate: readOnly('coordinates.firstObject'),
  endCoordinate: readOnly('coordinates.lastObject'),

  startPoint: computedPoint('coordinates.firstObject'),
  endPoint: computedPoint('coordinates.lastObject'),

  coordinatesObserver: observer('coordinates.[]', function () {
    this.adjustMapView();
    once(this.map, 'render');
  }),

  init() {
    this._super(...arguments);

    let startIcon = new Icon({
      anchor: [0.5, 1],
      src: '/images/marker-green.png',
    });
    startIcon.load();

    let endIcon = new Icon({
      anchor: [0.5, 1],
      src: '/images/marker.png',
    });
    endIcon.load();

    let startStyle = new Style({ image: startIcon });
    this.set('startStyle', startStyle);

    let endStyle = new Style({ image: endIcon });
    this.set('endStyle', endStyle);

    // activate coordinatesObserver
    this.get('coordinates');
  },

  didInsertElement() {
    this._super(...arguments);
    this.map.on('postcompose', this.onPostCompose);
  },

  willDestroyElement() {
    this._super(...arguments);
    this.map.un('postcompose', this.onPostCompose);
  },

  @action
  onPostCompose(e) {
    this.renderMarkers(e.vectorContext);
  },

  renderMarkers(context) {
    this.renderMarker(context, this.startStyle, this.startPoint);
    this.renderMarker(context, this.endStyle, this.endPoint);
  },

  renderMarker(context, style, coordinate) {
    if (coordinate) {
      context.setStyle(style);
      context.drawGeometry(coordinate);
    }
  },

  adjustMapView() {
    let coordinates = this.coordinates;
    if (coordinates) {
      let map = this.map;
      let extent = boundingExtent(coordinates);
      let padding = this.calculatePadding();
      map.getView().fit(extent, { padding });
    }
  },
});
