slFlightTracking = function(_map, fix_table_placeholder, baro_placeholder) {
  var flight_tracking = slFlightDisplay(_map,
                                        fix_table_placeholder,
                                        baro_placeholder);

  flight_tracking.init = function() {
    flight_tracking.setDefaultTime(-1);
    flight_tracking.setTime(-1);
  };

  /**
   * Retrieves all new traces for the displayed flights
   */
  flight_tracking.updateFlightsFromJSON = function() {
    flight_tracking.getFlights().each(function(flight) {
      var url = '/tracking/' + flight.getID() + '/json';

      $.ajax(url, {
        data: { last_update: flight.getLastUpdate() || null },
        success: function(data) {
          updateFlight(data);
          flight_tracking.update();
        }
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
    var flight = flight_tracking.getFlights().get(data.sfid);
    if (!flight)
      return;

    flight.update(data.points, data.barogram_t, data.barogram_h,
                  data.enl, data.elevations);
    flight_tracking.setTime(flight_tracking.getGlobalTime());
  }

  flight_tracking.init();
  return flight_tracking;
};
