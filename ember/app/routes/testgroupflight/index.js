import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import { computed } from '@ember/object';
import $ from 'jquery';
import FixCalc from '../utils/fix-calc';

export default Route.extend({
  ajax: service(),
  pinnedFlights: service(),
  units: service(),
  model: this.modelFor('testgroupflight'),
  firstpath: ajax.request(`/api/testgroupflight/${model.ids[0]}/json`),

  classNames: ['relative-fullscreen'],

  fixCalc: null,
//  flightPhase: null,

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
    fixCalc.addFlight(this.firstpath);
    this.set('fixCalc', fixCalc);
  },

  didInsertElement() {
    this._super(...arguments);
    let fixCalc = this.fixCalc;

    let sidebar = this.element.querySelector('#sidebar');
    let $sidebar = $(sidebar).sidebar();

//    let barogramPanel = this.element.querySelector('#barogram_panel');
//    let $barogramPanel = $(barogramPanel);

    let olScaleLine = this.element.querySelector('.ol-scale-line');
    let olAttribution = this.element.querySelector('.ol-attribution');

//    let resize = () => {
//      let bottom = Number(getComputedStyle(barogramPanel).bottom.replace('px', ''));
//      let height = barogramPanel.offsetHeight + bottom;
//
//      sidebar.style.bottom = `${height}px`;
//      olScaleLine.style.bottom = `${height}px`;
//      olAttribution.style.bottom = `${height}px`;
//    };
//
//    resize();
//    $barogramPanel.resize(resize);

    if (window.location.hash && sidebar.querySelector(`li > a[href="#${window.location.hash.substring(1)}"]`)) {
      $sidebar.open(window.location.hash.substring(1));
    } else if (window.innerWidth >= 768) {
      $sidebar.open('tab-overview');
    }

    let map = window.flightMap.get('map');
    //add rest of paths
    this.model.ids.slice(1).forEach(id => fixCalc.addFlightFromJSON(`/api/flights/${id}/json`));  //(1) includes 1 to end

    let extent = fixCalc.get('flights').getBounds();
    map.getView().fit(extent, { padding: this._calculatePadding() });

    this.get('pinnedFlights.pinned')
      .filter(id => id !== primaryId)
      .forEach(id => fixCalc.addFlightFromJSON(`/api/flights/${id}/json`));
  },

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

//    selectWingman(id) {
//      let fixCalc = this.fixCalc;
//      let pinnedFlights = this.pinnedFlights;
//
//      let flights = fixCalc.get('flights');
//      let matches = flights.filterBy('id', id);
//      if (matches.length !== 0) {
//        flights.removeObjects(matches);
//        pinnedFlights.unpin(id);
//      } else {
//        fixCalc.addFlightFromJSON(`/api/flights/${id}/json`);
//        pinnedFlights.pin(id);
//      }
//    },
//
    calculatePadding() {
      return this._calculatePadding();
    },
  }, //end actions

  _calculatePadding() {
    let sidebar = this.element.querySelector('#sidebar');
    let barogramPanel = this.element.querySelector('#barogram_panel');
    return [20, 20, barogramPanel.offsetHeight + 20, sidebar.offsetWidth + 20];
  },

});


