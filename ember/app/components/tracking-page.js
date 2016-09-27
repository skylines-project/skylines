import Ember from 'ember';
import ol from 'openlayers';

import slFlightDisplay from '../utils/flight-display';
import slMapClickHandler from '../utils/map-click-handler';

export default Ember.Component.extend({
  ajax: Ember.inject.service(),
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
    this.set('flightDisplay', flight_display);

    fixCalc.set('defaultTime', -1);
    fixCalc.set('time', -1);

    this.get('flights').forEach(flight => fixCalc.addFlight(flight));

    let extent = flights.getBounds();
    map.getView().fit(extent, map.getSize(), { padding: paddingFn() });

    // update flight track every 15 seconds
    this._scheduleUpdate();

    slMapClickHandler(map, flight_display);
  },

  willDestroyElement() {
    let updateTimer = this.get('updateTimer');
    if (updateTimer) {
      Ember.run.cancel(updateTimer);
    }
  },

  _scheduleUpdate() {
    this.set('updateTimer', Ember.run.later(() => this._update(), 15 * 1000));
  },

  _update() {
    let flightDisplay = this.get('flightDisplay');
    let flights = this.get('fixCalc.flights');
    let ajax = this.get('ajax');

    flights.forEach(flight => {
      let last_update = flight.get('last_update') || null;
      let data = { last_update };
      ajax.request(`/tracking/${flight.get('id')}/json`, { data }).then(data => {
        updateFlight(flights, data);
        flightDisplay.update();
      });
    });

    this._scheduleUpdate();
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
  if (!flight)
    return;

  let time_decoded = ol.format.Polyline.decodeDeltas(data.barogram_t, 1, 1);
  let lonlat = ol.format.Polyline.decodeDeltas(data.points, 2);
  let height_decoded = ol.format.Polyline.decodeDeltas(data.barogram_h, 1, 1);
  let enl_decoded = ol.format.Polyline.decodeDeltas(data.enl, 1, 1);
  let elev = ol.format.Polyline.decodeDeltas(data.elevations, 1, 1);

  // we skip the first point in the list because we assume it's the "linking"
  // fix between the data we already have and the data to add.
  if (time_decoded.length < 2) return;

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
    elevation: (elev[i] > -500) ? elev[i] : null,
  }));

  flight.get('fixes').pushObjects(fixes.slice(1));
  flight.get('elevations').pushObjects(elevations.slice(1));
}
