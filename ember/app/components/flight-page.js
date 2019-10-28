import Component from '@ember/component';
import { action, computed } from '@ember/object';
import { inject as service } from '@ember/service';

import $ from 'jquery';

import FixCalc from '../utils/fix-calc';
import FlighPhase from '../utils/flight-phase';

export default Component.extend({
  tagName: '',

  ajax: service(),
  pinnedFlights: service(),
  units: service(),

  fixCalc: null,
  flightPhase: null,

  timeInterval: computed('mapExtent', 'cesiumEnabled', function() {
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

    let flightPhase = FlighPhase.create({ fixCalc });
    this.set('flightPhase', flightPhase);
  },

  setup: action(function(element) {
    this.rootElement = element;

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
    } else if (window.innerWidth >= 768) {
      $sidebar.open('tab-overview');
    }

    let [primaryId, ...otherIds] = this.ids;

    let map = window.flightMap.get('map');

    otherIds.forEach(id => fixCalc.addFlightFromJSON(`/api/flights/${id}/json`));

    let extent = fixCalc.get('flights').getBounds();
    map.getView().fit(extent, { padding: this._calculatePadding() });

    this.get('pinnedFlights.pinned')
      .filter(id => id !== primaryId)
      .forEach(id => fixCalc.addFlightFromJSON(`/api/flights/${id}/json`));
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
        fixCalc.addFlightFromJSON(`/api/flights/${id}/json`);
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
