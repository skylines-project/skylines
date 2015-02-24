

/**
 * Retrieves all new traces for the displayed flights
 */
function updateFlightsFromJSON() {
  flights.each(function(flight) {
    var url = '/tracking/' + flight.getID() + '/json';

    $.ajax(url, {
      data: { last_update: flight.getLastUpdate() || null },
      success: function(data) {
        updateFlight(data);
        updateBaroData();
        updateBaroScale();
        baro.draw();
      }
    });
  });
}

/**
 * Updates a tracking flight.
 *
 * @param {Object} data The data returned by the JSON request.
 */

function updateFlight(data) {
  // find the flight to update
  var flight = flights.get(data.sfid);
  if (!flight)
    return;

  flight.update(data.points, data.barogram_t, data.barogram_h,
                data.enl, data.elevations);
  setTime(global_time);
}
