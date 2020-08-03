import EmberObject, { action } from '@ember/object';
import { bool, mapBy, min, max, map } from '@ember/object/computed';
import { tracked } from '@glimmer/tracking';

import { task } from 'ember-concurrency';

import Fix from '../utils/fix';
import slFlightCollection from '../utils/flight-collection';
import flightFromData from '../utils/flight-from-data';
import { nextAnimationFrame } from './raf';

/**
 * List of colors for flight path display
 * @type {Array<String>}
 */
const COLORS = ['#004bbd', '#bf0099', '#cf7c00', '#ff0000', '#00c994', '#ffff00'];

const PLAYBACK_SPEED = 50;

export default class FixCalc extends EmberObject {
  flights = slFlightCollection.create();

  /**
   * Global time, can be:
   * - null -> no time is set, don't show barogram crosshair/plane position
   * - -1 -> always show the latest time/fix for each flight
   * - >= 0 -> show the associated time in the barogram and on the map
   * @type {!Number}
   */
  @tracked time = null;

  /**
   * Default time - the time to set when no time is set
   * @type {!Number}
   */
  defaultTime = null;

  @bool('playbackTask.isRunning') isRunning;

  @mapBy('flights', 'startTime') startTimes;
  @min('startTimes') minStartTime;

  @mapBy('flights', 'endTime') endTimes;
  @max('endTimes') maxEndTime;

  @map('flights', function (flight) {
    return Fix.create({ flight, fixCalc: this });
  })
  fixes;

  @(task(function* () {
    let time = this.time;

    if (time === null || time === -1) {
      this.setTime(this.minStartTime);
    }

    let lastNow = performance.now();
    while (true) {
      yield nextAnimationFrame();

      let now = performance.now();
      let dt = now - lastNow;
      lastNow = now;

      time = this.time + dt * (PLAYBACK_SPEED / 1000);

      if (time > this.maxEndTime) {
        this.stopPlayback();
      }

      this.setTime(time);
    }
  }).drop())
  playbackTask;

  startPlayback() {
    this.playbackTask.perform();
  }

  stopPlayback() {
    this.playbackTask.cancelAll();
  }

  togglePlayback() {
    if (this.isRunning) {
      this.stopPlayback();
    } else {
      this.startPlayback();
    }
  }

  @action setTime(time) {
    this.time = time;
  }

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
  }

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
  }
}
