import Ember from 'ember';
import ol from 'openlayers';

import slFlight from '../utils/flight';
import slFlightCollection from '../utils/flight-collection';
import geographicDistance from '../utils/geo-distance';
import getNextSmallerIndex from '../utils/next-smaller-index';
import computedPoint from '../utils/computed-point';

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

  /**
   * Add a flight to the map and barogram.
   *
   * @param {Object} data The data received from the JSON request.
   */
  addFlight(data) {
    let flights = this.get('flights');

    let flight = slFlight.fromData(data);

    flight.set('color', COLORS[flights.get('length') % COLORS.length]);

    flights.pushObject(flight);
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

  _index: Ember.computed('flight.time', 't', function() {
    let t = this.get('t');
    if (!Ember.isNone(t)) {
      return getNextSmallerIndex(this.get('flight.time'), t);
    }
  }),

  t_prev: Ember.computed('flight.time', '_index', function() {
    let index = this.get('_index');
    if (!Ember.isNone(index)) {
      return this.get('flight.time')[index];
    }
  }),

  t_next: Ember.computed('flight.time', '_index', function() {
    let index = this.get('_index');
    if (!Ember.isNone(index)) {
      return this.get('flight.time')[index + 1];
    }
  }),

  time: Ember.computed.readOnly('t_prev'),

  coordinate: computedCoordinateAtM('flight.geometry', 't'),

  lon: Ember.computed.readOnly('coordinate.0'),
  lat: Ember.computed.readOnly('coordinate.1'),

  'alt-msl': Ember.computed('coordinate.2', 'flight.geoid', function() {
    let altitude = this.get('coordinate.2');
    if (!Ember.isNone(altitude)) {
      return altitude - this.get('flight.geoid');
    }
  }),

  'alt-gnd': Ember.computed('alt-msl', 'elevation', function() {
    let altitude = this.get('alt-msl');
    let elevation = this.get('elevation');
    if (!Ember.isNone(altitude) && !Ember.isNone(elevation)) {
      let value = altitude - elevation;
      return (value >= 0) ? value : 0;
    }
  }),

  point: computedPoint('coordinate'),

  heading: Ember.computed('_coordinate_prev', '_coordinate_next', function() {
    let prev = this.get('_coordinate_prev');
    let next = this.get('_coordinate_next');

    if (prev && next) {
      return Math.atan2(next[0] - prev[0], next[1] - prev[1]);
    }
  }),

  vario: Ember.computed('_coordinate_prev.2', '_coordinate_next.2', '_dt', function() {
    let prev = this.get('_coordinate_prev');
    let next = this.get('_coordinate_next');
    let dt = this.get('_dt');

    if (prev && next && dt) {
      return (next[2] - prev[2]) / dt;
    }
  }),

  speed: Ember.computed('_coordinate_prev', '_coordinate_next', '_dt', function() {
    let prev = this.get('_coordinate_prev');
    let next = this.get('_coordinate_next');
    let dt = this.get('_dt');

    if (prev && next && dt) {
      let loc_prev = ol.proj.transform(prev, 'EPSG:3857', 'EPSG:4326');
      let loc_next = ol.proj.transform(next, 'EPSG:3857', 'EPSG:4326');

      return geographicDistance(loc_next, loc_prev) / dt;
    }
  }),

  _dt: Ember.computed('t_prev', 't_next', function() {
    return this.get('t_next') - this.get('t_prev');
  }),

  _coordinate_prev: computedCoordinateAtM('flight.geometry', 't_prev'),
  _coordinate_next: computedCoordinateAtM('flight.geometry', 't_next'),

  elevation: Ember.computed('flight.elev_h.[]', '_elev_index', function() {
    let elev_h = this.get('flight.elev_h');
    if (elev_h) {
      return elev_h[this.get('_elev_index')];
    }
  }),

  _elev_index: Ember.computed('flight.elev_t.[]', 't', function() {
    let elev_t = this.get('flight.elev_t');
    if (elev_t) {
      return getNextSmallerIndex(elev_t, this.get('t'));
    }
  }),
});

Fix[Ember.NAME_KEY] = 'Fix';

function computedCoordinateAtM(geometryKey, timeKey) {
  return Ember.computed(geometryKey, timeKey, function() {
    let time = this.get(timeKey);
    if (!Ember.isNone(time)) {
      return this.get(geometryKey).getCoordinateAtM(time);
    }
  });
}
