import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { inject as service } from '@ember/service';

import $ from 'jquery';

import FixCalc from '../utils/fix-calc';
import getNextSmallerIndex from '../utils/next-smaller-index';

export default Component.extend({
  tagName: '',

  ajax: service(),
  pinnedFlights: service(),
  progress: service(),
  units: service(),

  fixCalc: null,
  highlightedTimeInterval: null,

  defaultTab: window.innerWidth >= 768 ? 'overview' : null,

  highlightedCoordinates: computed('highlightedTimeInterval', function () {
    let selection = this.highlightedTimeInterval;
    if (!selection) {
      return;
    }

    let { start, end } = selection;

    let flight = this.get('fixCalc.flights.firstObject');
    let times = flight.get('time');

    let start_index = getNextSmallerIndex(times, start);
    let end_index = getNextSmallerIndex(times, end);
    if (start_index >= end_index) {
      return;
    }

    let coordinates = flight.get('geometry').getCoordinates();
    return coordinates.slice(start_index, end_index + 1);
  }),

  timeInterval: computed('mapExtent', 'cesiumEnabled', function () {
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
    fixCalc.addFlight(this._primaryFlightPath);
    this.set('fixCalc', fixCalc);
  },

  setup: action(function (element) {
    this.rootElement = element;

    let fixCalc = this.fixCalc;

    let sidebar = this.rootElement.querySelector('#sidebar');

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

    let [primaryId, ...otherIds] = this.ids;

    let map = window.flightMap.get('map');

    otherIds.forEach(id => {
      let promise = fixCalc.addFlightFromJSON(`/api/flights/${id}/json`);
      this.progress.handle(promise);
    });

    let extent = fixCalc.get('flights').getBounds();
    map.getView().fit(extent, { padding: this._calculatePadding() });

    this.get('pinnedFlights.pinned')
      .filter(id => id !== primaryId)
      .forEach(id => {
        let promise = fixCalc.addFlightFromJSON(`/api/flights/${id}/json`);
        this.progress.handle(promise);
      });
  }),

  actions: {
    togglePlayback() {
      this.fixCalc.togglePlayback();
    },

    addFlight(data) {
      this.fixCalc.addFlight(data);
    },

    removeFlight(id) {
      let flights = this.get('fixCalc.flights');
      flights.removeObjects(flights.filterBy('id', id));
      this.pinnedFlights.unpin(id);
    },

    selectWingman(id) {
      let fixCalc = this.fixCalc;
      let pinnedFlights = this.pinnedFlights;

      let flights = fixCalc.get('flights');
      let matches = flights.filterBy('id', id);
      if (matches.length !== 0) {
        flights.removeObjects(matches);
        pinnedFlights.unpin(id);
      } else {
        let promise = fixCalc.addFlightFromJSON(`/api/flights/${id}/json`);
        this.progress.handle(promise);
        pinnedFlights.pin(id);
      }
    },

    calculatePadding() {
      return this._calculatePadding();
    },
  },

  _calculatePadding() {
    let sidebar = this.rootElement.querySelector('#sidebar');
    let barogramPanel = this.rootElement.querySelector('#barogram_panel');
    return [20, 20, barogramPanel.offsetHeight + 20, sidebar.offsetWidth + 20];
  },
});
