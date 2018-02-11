import { cancel, later } from '@ember/runloop';
import { computed } from '@ember/object';
import { inject as service } from '@ember/service';
import Component from '@ember/component';
import ol from 'openlayers';

import FixCalc from '../utils/fix-calc';

export default Component.extend({
  ajax: service(),
  units: service(),

  classNames: ['relative-fullscreen'],

  fixCalc: null,

  timeInterval: computed('mapExtent', 'cesiumEnabled', 'fixCalc.flights.[]', function() {
    if (this.get('cesiumEnabled')) { return null; }

    let extent = this.get('mapExtent');
    if (!extent) { return null; }

    let interval = this.get('fixCalc.flights').getMinMaxTimeInExtent(extent);

    return (interval.max === -Infinity) ? null : [interval.min, interval.max];
  }),

  init() {
    this._super(...arguments);

    let ajax = this.get('ajax');
    let units = this.get('units');

    let fixCalc = FixCalc.create({ ajax, units });
    this.set('fixCalc', fixCalc);
  },

  didInsertElement() {
    this._super(...arguments);
    let flights = this.get('flights');
    if (flights.length === 0) { return; }

    let fixCalc = this.get('fixCalc');

    let sidebar = this.$('#sidebar').sidebar();

    let resize = () => {
      let $barogramPanel = this.$('#barogram_panel');
      let bottom = Number($barogramPanel.css('bottom').replace('px', ''));
      let height = $barogramPanel.height() + bottom;
      sidebar.css('bottom', height);
      this.$('.ol-scale-line').css('bottom', height);
      this.$('.ol-attribution').css('bottom', height);
    };

    resize();
    this.$('#barogram_panel').resize(resize);

    if (window.location.hash &&
      sidebar.find(`li > a[href="#${window.location.hash.substring(1)}"]`).length !== 0) {
      sidebar.open(window.location.hash.substring(1));
    } else if (window.innerWidth >= 768 && flights.length > 1) {
      sidebar.open('tab-overview');
    }

    let map = window.flightMap.get('map');

    fixCalc.set('defaultTime', -1);
    fixCalc.set('time', -1);

    flights.forEach(flight => fixCalc.addFlight(flight));

    let extent = fixCalc.get('flights').getBounds();
    map.getView().fit(extent, { padding: this._calculatePadding() });

    // update flight track every 15 seconds
    this._scheduleUpdate();
  },

  willDestroyElement() {
    this._super(...arguments);
    let updateTimer = this.get('updateTimer');
    if (updateTimer) {
      cancel(updateTimer);
    }
  },

  actions: {
    togglePlayback() {
      this.get('fixCalc').togglePlayback();
    },

    removeFlight(id) {
      let flights = this.get('fixCalc.flights');
      flights.removeObjects(flights.filterBy('id', id));
    },

    calculatePadding() {
      return this._calculatePadding();
    },
  },

  _scheduleUpdate() {
    this.set('updateTimer', later(() => this._update(), 15 * 1000));
  },

  _update() {
    let flights = this.get('fixCalc.flights');
    let ajax = this.get('ajax');

    flights.forEach(flight => {
      let last_update = flight.get('last_update') || null;
      let data = { last_update };
      ajax.request(`/api/live/${flight.get('id')}/json`, { data }).then(data => {
        updateFlight(flights, data);
      }).catch(() => {
        // ignore update errors
      });
    });

    this._scheduleUpdate();
  },

  _calculatePadding() {
    return [20, 20, this.$('#barogram_panel').height() + 20, this.$('#sidebar').width() + 20];
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
  if (!flight) { return; }

  let time_decoded = ol.format.Polyline.decodeDeltas(data.barogram_t, 1, 1);
  let lonlat = ol.format.Polyline.decodeDeltas(data.points, 2);
  let height_decoded = ol.format.Polyline.decodeDeltas(data.barogram_h, 1, 1);
  let enl_decoded = ol.format.Polyline.decodeDeltas(data.enl, 1, 1);
  let elev = ol.format.Polyline.decodeDeltas(data.elevations, 1, 1);

  // we skip the first point in the list because we assume it's the "linking"
  // fix between the data we already have and the data to add.
  if (time_decoded.length < 2) { return; }

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
