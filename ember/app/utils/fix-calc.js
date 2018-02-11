import { later, cancel } from '@ember/runloop';
import { bool, mapBy, min, max, map } from '@ember/object/computed';
import EmberObject from '@ember/object';

import flightFromData from '../utils/flight-from-data';
import slFlightCollection from '../utils/flight-collection';
import Fix from '../utils/fix';

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

export default EmberObject.extend({
  ajax: null,
  units: null,

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
    let time = this.get('time');

    if (time === null || time === -1) {
      this.set('time', this.get('minStartTime'));
    }

    this.set('timer', later(this, 'onTick', 50));
  },

  stopPlayback() {
    let timer = this.get('timer');
    if (timer) {
      cancel(timer);
      this.set('timer', null);
    }
  },

  togglePlayback() {
    if (this.get('isRunning')) {
      this.stopPlayback();
    } else {
      this.startPlayback();
    }
  },

  onTick() {
    let time = this.get('time') + 1;

    if (time > this.get('maxEndTime')) {
      this.stopPlayback();
    }

    this.set('time', time);
    this.set('timer', later(this, 'onTick', 50));
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

    let flight = flightFromData(data, this.get('units'));

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
    let flights = this.get('flights');

    let data = await this.get('ajax').request(url);
    if (!flights.findBy('id', data.sfid)) {
      this.addFlight(data);
    }
  },
});
