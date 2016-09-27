import Ember from 'ember';

import slFlightDisplay from '../utils/flight-display';
import slMapClickHandler from '../utils/map-click-handler';

export default Ember.Component.extend({
  fixCalc: Ember.inject.service(),
  pinnedFlights: Ember.inject.service(),

  classNames: ['olFullscreen'],

  didInsertElement() {
    let fixCalc = this.get('fixCalc');

    let sidebar = this.$('#sidebar').sidebar();

    this.$('#barogram_panel').resize(() => {
      let height = this.$('#barogram_panel').height() + 10;
      sidebar.css('bottom', height);
      this.$('.ol-scale-line').css('bottom', height);
      this.$('.ol-attribution').css('bottom', height);
    });

    if (window.location.hash &&
      sidebar.find(`li > a[href="#${window.location.hash.substring(1)}"]`).length != 0) {
      sidebar.open(window.location.hash.substring(1));
    }

    let paddingFn = window.paddingFn = () => [20, 20, this.$('#barogram_panel').height() + 20, sidebar.width() + 20];

    let [primaryId, ...otherIds] = this.get('ids');

    let map = window.flightMap.get('map');

    fixCalc.addFlightFromJSON(`/flights/${primaryId}/json`, false);
    otherIds.forEach(otherId => {
      fixCalc.addFlightFromJSON(`/flights/${otherId}/json`);
    });

    let extent = fixCalc.get('flights').getBounds();
    map.getView().fit(extent, map.getSize(), { padding: paddingFn() });

    this.get('pinnedFlights.pinned').filter(function(id) {
      return id !== primaryId;
    }).forEach(function(id) {
      fixCalc.addFlightFromJSON(`/flights/${id}/json`);
    });

    let flight_display = slFlightDisplay.create({
      fixCalc,
      flightMap: window.flightMap,
      fix_table: window.fixTable,
      baro: window.barogram,
    });

    slMapClickHandler(map, flight_display);
  },

  actions: {
    selectWingman(id) {
      let fixCalc = this.get('fixCalc');
      let pinnedFlights = this.get('pinnedFlights');

      let flights = fixCalc.get('flights');
      let matches = flights.filterBy('id', id);
      if (matches.length !== 0) {
        flights.removeObjects(matches);
        pinnedFlights.unpin(id);
      } else {
        fixCalc.addFlightFromJSON(`/flights/${id}/json`);
        pinnedFlights.pin(id);
      }
    },
  },
});
