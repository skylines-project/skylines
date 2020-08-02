import Component from '@ember/component';
import { action, observer } from '@ember/object';
import { readOnly } from '@ember/object/computed';
import { once } from '@ember/runloop';

import Icon from 'ol/style/Icon';
import Style from 'ol/style/Style';

import computedPoint from '../computed/computed-point';

const START_ICON = new Icon({
  anchor: [0.5, 1],
  src: '/images/marker-green.png',
});

const END_ICON = new Icon({
  anchor: [0.5, 1],
  src: '/images/marker.png',
});

START_ICON.load();
END_ICON.load();

const START_STYLE = new Style({ image: START_ICON });
const END_STYLE = new Style({ image: END_ICON });

export default Component.extend({
  tagName: '',

  map: null,
  paddingFn: null,
  coordinates: null,

  startCoordinate: readOnly('coordinates.firstObject'),
  endCoordinate: readOnly('coordinates.lastObject'),

  startPoint: computedPoint('coordinates.firstObject'),
  endPoint: computedPoint('coordinates.lastObject'),

  coordinatesObserver: observer('coordinates.[]', function () {
    once(this.map, 'render');
  }),

  init() {
    this._super(...arguments);

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
    this.renderMarker(context, START_STYLE, this.startPoint);
    this.renderMarker(context, END_STYLE, this.endPoint);
  },

  renderMarker(context, style, coordinate) {
    if (coordinate) {
      context.setStyle(style);
      context.drawGeometry(coordinate);
    }
  },
});
