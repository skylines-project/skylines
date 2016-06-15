/* globals ol */

import Ember from 'ember';

/**
 * A handler to display plane icons on the map.
 */
export default Ember.Object.extend({
  map: null,
  flights: null,

  showPlane(flight, fix_data) {
    var marker = flight.get('marker');

    // add plane marker if more than one flight on the map
    if (this.get('flights.length') > 1) {
      if (!marker) {
        var badge = Ember.$('<span class="badge plane_marker" ' +
          'style="display: inline-block; text-align: center; ' +
          'background: ' + flight.get('color') + ';">' +
          flight.getWithDefault('competition_id', '') +
          '</span>');

        marker = new ol.Overlay({
          element: badge.get(0)
        });

        this.get('map').addOverlay(marker);
        flight.set('marker', marker);

        marker.setOffset([badge.width(), -40]);
      }

      marker.setPosition(fix_data.get('coordinate'));
    }
  },

  hidePlane(flight) {
    var marker = flight.get('marker');
    if (marker) {
      this.get('map').removeOverlay(marker);
      flight.set('marker', null);
    }
  },

  hideAllPlanes() {
    this.get('flights').forEach(flight => this.hidePlane(flight));
  }
});
