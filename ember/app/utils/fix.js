import EmberObject, { computed } from '@ember/object';
import { readOnly } from '@ember/object/computed';
import Ember from 'ember';

import ol from 'openlayers';

import computedPoint from '../computed/computed-point';
import safeComputed from '../computed/safe-computed';
import geographicDistance from '../utils/geo-distance';
import getNextSmallerIndex from '../utils/next-smaller-index';

let Fix = EmberObject.extend({
  fixCalc: null,

  _t: readOnly('fixCalc.time'),

  t: computed('_t', 'flight.{startTime,endTime}', function() {
    let _t = this._t;
    if (_t === -1) {
      return this.get('flight.endTime');
    } else if (_t >= this.get('flight.startTime') && _t <= this.get('flight.endTime')) {
      return _t;
    }
  }),

  _index: safeComputed('t', 'flight.time', (t, time) => getNextSmallerIndex(time, t)),

  t_prev: safeComputed('_index', 'flight.time', (index, time) => time[index]),
  t_next: safeComputed('_index', 'flight.time', (index, time) => time[index + 1]),

  time: readOnly('t_prev'),

  coordinate: safeComputed('t', 'flight.geometry', (time, geometry) => geometry.getCoordinateAtM(time)),

  lon: readOnly('coordinate.0'),
  lat: readOnly('coordinate.1'),

  'alt-msl': safeComputed('coordinate.2', 'flight.geoid', (altitude, geoid) => altitude - geoid),

  'alt-gnd': safeComputed('alt-msl', 'elevation', (altitude, elevation) => {
    let value = altitude - elevation;
    return value >= 0 ? value : 0;
  }),

  point: computedPoint('coordinate'),
  pointXY: computedPoint('coordinate', 'XY'),

  heading: safeComputed('_coordinate_prev', '_coordinate_next', (prev, next) =>
    Math.atan2(next[0] - prev[0], next[1] - prev[1]),
  ),

  vario: safeComputed('_coordinate_prev.2', '_coordinate_next.2', '_dt', (prev, next, dt) => (next - prev) / dt),

  speed: safeComputed('_coordinate_prev', '_coordinate_next', '_dt', (prev, next, dt) => {
    let loc_prev = ol.proj.transform(prev, 'EPSG:3857', 'EPSG:4326');
    let loc_next = ol.proj.transform(next, 'EPSG:3857', 'EPSG:4326');

    return geographicDistance(loc_next, loc_prev) / dt;
  }),

  _dt: safeComputed('t_prev', 't_next', (prev, next) => next - prev),

  _coordinate_prev: safeComputed('t_prev', 'flight.geometry', (time, geometry) => geometry.getCoordinateAtM(time)),
  _coordinate_next: safeComputed('t_next', 'flight.geometry', (time, geometry) => geometry.getCoordinateAtM(time)),

  elevation: safeComputed('flight.elev_h', '_elev_index', (elev_h, index) => elev_h[index]),

  _elev_index: safeComputed('flight.elev_t', 't', (elev_t, t) => getNextSmallerIndex(elev_t, t)),
});

Fix[Ember.NAME_KEY] = 'Fix';

export default Fix;
