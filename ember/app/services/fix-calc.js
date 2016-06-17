import Ember from 'ember';
import ol from 'openlayers';

import flightFromData from '../utils/flight-from-data';
import slFlightCollection from '../utils/flight-collection';
import geographicDistance from '../utils/geo-distance';
import getNextSmallerIndex from '../utils/next-smaller-index';
import computedPoint from '../utils/computed-point';
import safeComputed from '../utils/safe-computed';

/**
 * List of colors for flight path display
 * @type {Array<String>}
 */
const COLORS = [
  '#004bbd',
  '#bf0099',
  '#cf7c00',
  '#ff0000',
  '#00c994',
  '#ffff00',
];

export default Ember.Service.extend({
  flights: [],

  /*
   * Global time, can be:
   * null -> no time is set, don't show barogram crosshair/plane position
   * -1 -> always show the latest time/fix for each flight
   * >= 0 -> show the associated time in the barogram and on the map
   * @type {!Number}
   */
  time: null,

  /**
   * Default time - the time to set when no time is set
   * @type {!Number}
   */
  defaultTime: null,

  timer: null,

  isRunning: Ember.computed.bool('timer'),

  startTimes: Ember.computed.mapBy('flights', 'startTime'),
  minStartTime: Ember.computed.min('startTimes'),

  endTimes: Ember.computed.mapBy('flights', 'endTime'),
  maxEndTime: Ember.computed.max('endTimes'),

  fixes: Ember.computed.map('flights', function(flight) {
    return Fix.create({ flight, fixCalc: this });
  }),

  init() {
    this._super(...arguments);
    window.fixCalcService = this;

    this.set('flights', slFlightCollection.create());
  },

  startPlayback() {
    let time = this.get('time');

    if (time === null || time === -1) {
      this.set('time', this.get('minStartTime'));
    }

    this.set('timer', Ember.run.later(this, 'onTick', 50));
  },

  stopPlayback() {
    let timer = this.get('timer');
    if (timer) {
      Ember.run.cancel(timer);
      this.set('timer', null);
    }
  },

  onTick() {
    let time = this.get('time') + 1;

    if (time > this.get('maxEndTime')) {
      this.stopPlayback();
    }

    this.set('time', time);
    this.set('timer', Ember.run.later(this, 'onTick', 50));
  },

  resetTime() {
    this.set('time', this.get('defaultTime'));
  },

  /**
   * Add a flight to the map and barogram.
   *
   * @param {Object} data The data received from the JSON request.
   */
  addFlight(data) {
    let flights = this.get('flights');

    let flight = flightFromData(data);

    flight.set('color', COLORS[flights.get('length') % COLORS.length]);

    flights.pushObject(flight);
  },

  /**
   * Perform a JSON request to get a flight.
   *
   * @param {String} url URL to fetch.
   * @param {Boolean=} opt_async do asynchronous request (defaults true)
   */
  addFlightFromJSON(url, opt_async) {
    let flights = this.get('flights');

    Ember.$.ajax(url, {
      async: (typeof opt_async === undefined) || opt_async === true,
      success: data => {
        if (flights.findBy('id', data.sfid))
          return;

        this.addFlight(data);
      },
    });
  },
});

let Fix = Ember.Object.extend({
  fixCalc: null,

  _t: Ember.computed.readOnly('fixCalc.time'),

  t: Ember.computed('_t', 'flight.{startTime,endTime}', function() {
    let _t = this.get('_t');
    if (_t === -1) {
      return this.get('flight.endTime');
    } else if (_t >= this.get('flight.startTime') && _t <= this.get('flight.endTime')) {
      return _t;
    }
  }),

  _index: safeComputed('t', 'flight.time', (t, time) => getNextSmallerIndex(time, t)),

  t_prev: safeComputed('_index', 'flight.time', (index, time) => time[index]),
  t_next: safeComputed('_index', 'flight.time', (index, time) => time[index + 1]),

  time: Ember.computed.readOnly('t_prev'),

  coordinate: safeComputed('t', 'flight.geometry', (time, geometry) => geometry.getCoordinateAtM(time)),

  lon: Ember.computed.readOnly('coordinate.0'),
  lat: Ember.computed.readOnly('coordinate.1'),

  'alt-msl': safeComputed('coordinate.2', 'flight.geoid', (altitude, geoid) => altitude - geoid),

  'alt-gnd': safeComputed('alt-msl', 'elevation', (altitude, elevation) => {
    let value = altitude - elevation;
    return (value >= 0) ? value : 0;
  }),

  point: computedPoint('coordinate'),
  pointXY: computedPoint('coordinate', 'XY'),

  heading: safeComputed('_coordinate_prev', '_coordinate_next',
    (prev, next) => Math.atan2(next[0] - prev[0], next[1] - prev[1])),

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
