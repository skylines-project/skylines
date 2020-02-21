import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import { computed } from '@ember/object';
import $ from 'jquery';
import FixCalc from '../utils/fix-calc';
import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),
  pinnedFlights: service(),
  units: service(),
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
    console.log(this.club.name)
    let ajax = this.ajax;
    let units = this.units;
//    let data = this.data
    let fixCalc = FixCalc.create({ ajax, units });
    if (this.firstPath) {console.log('firstPath'),console.log(this.firstPath.sfid)}
    else {console.log('not firstPath')}
    if (this.firstData) {console.log('firstData'),console.log(this.firstData.flight.id)}
    else {console.log('not firstData')}
    fixCalc.addFlight(this.firstPath);
    this.set('fixCalc', fixCalc);
    console.log('test1b')
  },

  didInsertElement() {
    this._super(...arguments);
    let fixCalc = this.fixCalc;

    let sidebar = this.element.querySelector('#sidebar');
    let $sidebar = $(sidebar).sidebar();

    let olScaleLine = this.element.querySelector('.ol-scale-line');
    let olAttribution = this.element.querySelector('.ol-attribution');

    if (window.location.hash && sidebar.querySelector(`li > a[href="#${window.location.hash.substring(1)}"]`)) {
      $sidebar.open(window.location.hash.substring(1));
    } else if (window.innerWidth >= 768) {
      $sidebar.open('tab-overview');
    }

    let map = window.flightMap.get('map');
    //add rest of paths
//    this.ids.slice(1).forEach(id => fixCalc.addFlightFromJSON(`/api/flights/${id}/json`));  //(1) includes 1 to end

    let extent = fixCalc.get('flights').getBounds();
    map.getView().fit(extent, { padding: this._calculatePadding() });

    this.get('pinnedFlights.pinned')
      .filter(id => id !== primaryId)
      .forEach(id => fixCalc.addFlightFromJSON(`/api/flights/${id}/json`));
  },

  actions: {

    togglePlayback() {
    console.log('test2');
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


    calculatePadding() {
      return this._calculatePadding();
    },
  }, //end actions

  _calculatePadding() {
    let sidebar = this.element.querySelector('#sidebar');
//    let barogramPanel = this.element.querySelector('#barogram_panel');
    return [20, 20, 20, sidebar.offsetWidth + 20];
  },

});
