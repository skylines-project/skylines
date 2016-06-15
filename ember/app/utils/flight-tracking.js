/* globals $, ol */

export default function slFlightTracking(flight_display, flights) {
  var flight_tracking = {};

  flight_tracking.init = function() {
    flight_display.setDefaultTime(-1);
    flight_display.setTime(-1);
  };

  /**
   * Retrieves all new traces for the displayed flights
   */
  flight_tracking.updateFlightsFromJSON = function() {
    flights.forEach(function(flight) {
      var url = '/tracking/' + flight.getID() + '/json';

      $.ajax(url, {
        data: { last_update: flight.get('last_update') || null },
        success: function(data) {
          updateFlight(data);
          flight_display.update();
        },
      });
    });
  };

  /**
   * Updates a tracking flight.
   *
   * @param {Object} data The data returned by the JSON request.
   */

  function updateFlight(data) {
    // find the flight to update
    var flight = flights.findBy('id', data.sfid);
    if (!flight)
      return;

    var time_decoded = ol.format.Polyline.decodeDeltas(data.barogram_t, 1, 1);
    var lonlat = ol.format.Polyline.decodeDeltas(data.points, 2);
    var height_decoded = ol.format.Polyline.decodeDeltas(data.barogram_h, 1, 1);
    var enl_decoded = ol.format.Polyline.decodeDeltas(data.enl, 1, 1);
    var elev = ol.format.Polyline.decodeDeltas(data.elevations, 1, 1);

    // we skip the first point in the list because we assume it's the "linking"
    // fix between the data we already have and the data to add.
    if (time_decoded.length < 2) return;

    var geoid = flight.get('geoid');

    var fixes = time_decoded.map(function(timestamp, i) {
      return {
        time: timestamp,
        longitude: lonlat[i * 2],
        latitude: lonlat[i * 2 + 1],
        altitude: height_decoded[i] + geoid,
        enl: enl_decoded[i],
      };
    });

    var elevations = time_decoded.map(function(timestamp, i) {
      var elevation = elev[i];

      return {
        time: timestamp,
        elevation: (elevation > -500) ? elevation : null,
      }
    });

    flight.get('fixes').pushObjects(fixes.slice(1));
    flight.get('elevations').pushObjects(elevations.slice(1));
  }

  flight_tracking.init();
  return flight_tracking;
}
