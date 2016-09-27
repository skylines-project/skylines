import Ember from 'ember';

import slFlightDisplay from '../utils/flight-display';
import slFlightTracking from '../utils/flight-tracking';
import slMapClickHandler from '../utils/map-click-handler';

export default Ember.Component.extend({
  fixCalc: Ember.inject.service(),

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

    let map = window.flightMap.get('map');

    let flights = fixCalc.get('flights');

    let flight_display = slFlightDisplay.create({
      fixCalc,
      flightMap: window.flightMap,
      fix_table: window.fixTable,
      baro: window.barogram,
    });

    this.set('flightTracking', slFlightTracking.create({ flight_display, flights }));

    fixCalc.set('defaultTime', -1);
    fixCalc.set('time', -1);

    this.get('flights').forEach(flight => fixCalc.addFlight(flight));

    let extent = flights.getBounds();
    map.getView().fit(extent, map.getSize(), { padding: paddingFn() });

    // update flight track every 15 seconds
    this._scheduleUpdate();

    slMapClickHandler(map, flight_display);
  },

  _scheduleUpdate() {
    Ember.run.later(() => this._update(), 15 * 1000);
  },

  _update() {
    this.get('flightTracking').updateFlightsFromJSON();
    this._scheduleUpdate();
  },
});
