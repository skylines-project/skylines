import EmberObject from '@ember/object';
import { bool, mapBy, min, max, map } from '@ember/object/computed';
import { later, cancel } from '@ember/runloop';

import Fix from '../utils/fix';
import slFlightCollection from '../utils/flight-collection';
import flightFromData from '../utils/flight-from-data';

/**
 * List of colors for flight path display
 * @type {Array<String>}
 */
//const COLORS = ['#004bbd', '#bf0099', '#cf7c00', '#ff0000', '#00c994', '#ffff00'];

//matplotlib colors used below
//['dodgerblue','orange','red','gold','fuchsia','aqua',
//'green','blue','darkblue','teal','black','darkred',
//'chocolate','limegreen','crimson','deepskyblue','springgreen',
//'cornflowerblue','hotpink','turquoise',
//'lightgrey','purple','orangered','firebrick','lavender',
//'mediumblue','antiquewhite','salmon','mistyrose','pink','goldenrod']

const COLORS =
[
'#1e90ff','#ffa500','#ff0000','#ffd700','#ff00ff','#00ffff',
'#008000','#0000ff','#008080','#000000','#8b0000',
'#d2691e','#32cd32','#dc143c','#00bfff','#00ff7f',
'#6495ed','#ff69b4','#40e0d0','#000000',
'#d3d3d3','#800080','#ff4500','#b22222','#e6e6fa',
'#0000cd','#faebd7','#fa8072','#ffe4e1','#ffc0cb','#daa520'
]

export default EmberObject.extend({
  ajax: null,
  units: null,

  // flights: [],

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

  isRunning: bool('timer'),

  startTimes: mapBy('flights', 'startTime'),
  minStartTime: min('startTimes'),

  endTimes: mapBy('flights', 'endTime'),
  maxEndTime: max('endTimes'),

  fixes: map('flights', function(flight) {
    return Fix.create({ flight, fixCalc: this });
  }),

  init() {
    this._super(...arguments);
    this.set('flights', slFlightCollection.create());
  },

  startPlayback() {
    let time = this.time;

    if (time === null || time === -1) {
      this.set('time', this.minStartTime);
    }

    this.set('timer', later(this, 'onTick', 50));
  },

  stopPlayback() {
    let timer = this.timer;
    if (timer) {
      cancel(timer);
      this.set('timer', null);
    }
  },

  togglePlayback() {
    if (this.isRunning) {
      this.stopPlayback();
    } else {
      this.startPlayback();
    }
  },

  onTick() {
    let time = this.time + 1;

    if (time > this.maxEndTime) {
      this.stopPlayback();
    }

    this.set('time', time);
    this.set('timer', later(this, 'onTick', 50));
  },

  resetTime() {
    this.set('time', this.defaultTime);
  },

  /**
   * Add a flight to the map and barogram.
   *
   * @param {Object} data The data received from the JSON request.
   */
  addFlight(data) {
    let flights = this.flights;

    let flight = flightFromData(data, this.units);

    if (data.additional && data.additional.color) {
      flight.set('color', data.additional.color);
    } else {
      flight.set('color', COLORS[flights.get('length') % COLORS.length]);
    }

    flights.pushObject(flight);
  },

  /**
   * Perform a JSON request to get a flight.
   *
   * @param {String} url URL to fetch.
   */
  async addFlightFromJSON(url) {
    let flights = this.flights;

    let data = await this.ajax.request(url);
    if (!flights.findBy('id', data.sfid)) {
      this.addFlight(data);
    }
  },
});
