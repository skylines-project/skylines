import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { inject as service } from '@ember/service';

import { task, rawTimeout } from 'ember-concurrency';
import $ from 'jquery';
import ol from 'openlayers';

import FixCalc from '../utils/fix-calc';

export default Component.extend({
  tagName: '',
  ajax: service(),

  units: service(),

  fixCalc: null,

  timeInterval: computed('mapExtent', 'cesiumEnabled', 'fixCalc.flights.[]', function() {
    if (this.cesiumEnabled) {
      return null;
    }

    let extent = this.mapExtent;
    if (!extent) {
      return null;
    }

    let interval = this.get('fixCalc.flights').getMinMaxTimeInExtent(extent);

    return interval.max === -Infinity ? null : [interval.min, interval.max];
  }),

  init() {
    this._super(...arguments);

    let ajax = this.ajax;
    let units = this.units;

    let fixCalc = FixCalc.create({ ajax, units });
    this.set('fixCalc', fixCalc);
  },

  setup: action(function(element) {
    this.rootElement = element;

    let flights = this.flights;
    if (flights.length === 0) {
      return;
    }

    let fixCalc = this.fixCalc;

    let sidebar = this.rootElement.querySelector('#sidebar');
    let $sidebar = $(sidebar).sidebar();

    let barogramPanel = this.rootElement.querySelector('#barogram_panel');
    let $barogramPanel = $(barogramPanel);

    let olScaleLine = this.rootElement.querySelector('.ol-scale-line');
    let olAttribution = this.rootElement.querySelector('.ol-attribution');

    let resize = () => {
      let bottom = Number(getComputedStyle(barogramPanel).bottom.replace('px', ''));
      let height = barogramPanel.offsetHeight + bottom;

      sidebar.style.bottom = `${height}px`;
      olScaleLine.style.bottom = `${height}px`;
      olAttribution.style.bottom = `${height}px`;
    };

    resize();
    $barogramPanel.resize(resize);

    if (window.location.hash && sidebar.querySelector(`li > a[href="#${window.location.hash.substring(1)}"]`)) {
      $sidebar.open(window.location.hash.substring(1));
    } else if (window.innerWidth >= 768 && flights.length > 1) {
      $sidebar.open('tab-overview');
    }

    let map = window.flightMap.get('map');

    fixCalc.set('defaultTime', -1);
    fixCalc.set('time', -1);

    flights.forEach(flight => fixCalc.addFlight(flight));

    let extent = fixCalc.get('flights').getBounds();
    map.getView().fit(extent, { padding: this._calculatePadding() });

    this.updateLoopTask.perform();
  }),

  // update flight track every 15 seconds
  updateLoopTask: task(function*() {
    while (true) {
      yield rawTimeout(15 * 1000);
      this._update();
    }
  }),

  actions: {
    togglePlayback() {
      this.fixCalc.togglePlayback();
    },

    removeFlight(id) {
      let flights = this.get('fixCalc.flights');
      flights.removeObjects(flights.filterBy('id', id));
    },

    calculatePadding() {
      return this._calculatePadding();
    },
  },

  _update() {
    let flights = this.get('fixCalc.flights');
    let ajax = this.ajax;

    flights.forEach(flight => {
      let last_update = flight.get('last_update') || null;
      let data = { last_update };
      ajax
        .request(`/api/live/${flight.get('id')}/json`, { data })
        .then(data => {
          updateFlight(flights, data);
        })
        .catch(() => {
          // ignore update errors
        });
    });
  },

  _calculatePadding() {
    let sidebar = this.rootElement.querySelector('#sidebar');
    let barogramPanel = this.rootElement.querySelector('#barogram_panel');
    return [20, 20, barogramPanel.offsetHeight + 20, sidebar.offsetWidth + 20];
  },
});

/**
 * Updates a tracking flight.
 *
 * @param {Object} data The data returned by the JSON request.
 */
function updateFlight(flights, data) {
  // find the flight to update
  let flight = flights.findBy('id', data.sfid);
  if (!flight) {
    return;
  }

  let time_decoded = ol.format.Polyline.decodeDeltas(data.barogram_t, 1, 1);
  let lonlat = ol.format.Polyline.decodeDeltas(data.points, 2);
  let height_decoded = ol.format.Polyline.decodeDeltas(data.barogram_h, 1, 1);
  let enl_decoded = ol.format.Polyline.decodeDeltas(data.enl, 1, 1);
  let elev = ol.format.Polyline.decodeDeltas(data.elevations, 1, 1);

  // we skip the first point in the list because we assume it's the "linking"
  // fix between the data we already have and the data to add.
  if (time_decoded.length < 2) {
    return;
  }

  let geoid = flight.get('geoid');

  let fixes = time_decoded.map((timestamp, i) => ({
    time: timestamp,
    longitude: lonlat[i * 2],
    latitude: lonlat[i * 2 + 1],
    altitude: height_decoded[i] + geoid,
    enl: enl_decoded[i],
  }));

  let elevations = time_decoded.map((timestamp, i) => ({
    time: timestamp,
    elevation: elev[i] > -500 ? elev[i] : null,
  }));

  flight.get('fixes').pushObjects(fixes.slice(1));
  flight.get('elevations').pushObjects(elevations.slice(1));
}
