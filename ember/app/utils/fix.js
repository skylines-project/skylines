import EmberObject, { computed } from '@ember/object';
import { readOnly } from '@ember/object/computed';

import { transform } from 'ol/proj';

import computedPoint from '../computed/computed-point';
import safeComputed from '../computed/safe-computed';
import geographicDistance from '../utils/geo-distance';
import getNextSmallerIndex from '../utils/next-smaller-index';

export default class Fix extends EmberObject {
  @readOnly('fixCalc.time') _t;

  @computed('_t', 'flight.{startTime,endTime}')
  get t() {
    let _t = this._t;
    if (_t === -1) {
      return this.get('flight.endTime');
    } else if (_t >= this.get('flight.startTime') && _t <= this.get('flight.endTime')) {
      return _t;
    }
  }

  @safeComputed('t', 'flight.time', (t, time) => getNextSmallerIndex(time, t)) _index;

  @safeComputed('_index', 'flight.time', (index, time) => time[index]) t_prev;
  @safeComputed('_index', 'flight.time', (index, time) => time[index + 1]) t_next;

  @readOnly('t_prev') time;

  @safeComputed('t', 'flight.geometry', (time, geometry) => geometry.getCoordinateAtM(time)) coordinate;

  @readOnly('coordinate.0') lon;
  @readOnly('coordinate.1') lat;

  @safeComputed('coordinate.2', 'flight.geoid', (altitude, geoid) => altitude - geoid) altitudeMSL;

  @safeComputed('altitudeMSL', 'elevation', (altitude, elevation) => {
    let value = altitude - elevation;
    return value >= 0 ? value : 0;
  })
  altitudeGND;

  @computedPoint('coordinate') point;
  @computedPoint('coordinate', 'XY') pointXY;

  @safeComputed('_coordinate_prev', '_coordinate_next', (prev, next) =>
    Math.atan2(next[0] - prev[0], next[1] - prev[1]),
  )
  heading;

  @safeComputed('_coordinate_prev.2', '_coordinate_next.2', '_dt', (prev, next, dt) => (next - prev) / dt) vario;

  @safeComputed('_coordinate_prev', '_coordinate_next', '_dt', (prev, next, dt) => {
    let loc_prev = transform(prev, 'EPSG:3857', 'EPSG:4326');
    let loc_next = transform(next, 'EPSG:3857', 'EPSG:4326');

    return geographicDistance(loc_next, loc_prev) / dt;
  })
  speed;

  @safeComputed('t_prev', 't_next', (prev, next) => next - prev) _dt;

  @safeComputed('t_prev', 'flight.geometry', (time, geometry) => geometry.getCoordinateAtM(time)) _coordinate_prev;
  @safeComputed('t_next', 'flight.geometry', (time, geometry) => geometry.getCoordinateAtM(time)) _coordinate_next;

  @safeComputed('flight.elev_h', '_elev_index', (elev_h, index) => elev_h[index]) elevation;

  @safeComputed('flight.elev_t', 't', (elev_t, t) => getNextSmallerIndex(elev_t, t)) _elev_index;
}
