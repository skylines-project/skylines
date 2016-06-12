slFlightTracking = function(_map, fix_table_placeholder, baro_placeholder) {
  var flight_tracking = slFlightDisplay(_map,
                                        fix_table_placeholder,
                                        baro_placeholder);

  flight_tracking.init = function() {
    flight_tracking.setDefaultTime(-1);
    flight_tracking.setTime(-1);
    flight_tracking.getFlights().urlRoot = '/tracking/';
    flight_tracking.getFlights().on('sync', updated);
  };

  /**
   * Retrieves all new traces for the displayed flights
   */
  flight_tracking.updateFlightsFromJSON = function() {
    flight_tracking.getFlights().each(function(flight) {
      flight.update();
    });
  };

  function updated() {
    flight_tracking.setTime(flight_tracking.getGlobalTime());
  };

  flight_tracking.init();
  return flight_tracking;
};
