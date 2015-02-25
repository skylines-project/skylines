

/**
 * Retrieves all new traces for the displayed flights
 */
function updateFlightsFromJSON() {
  flights.each(function(flight) {
    var url = '/tracking/' + flight.getID() + '/json';

    $.ajax(url, {
      data: { last_update: flight.getLastUpdate() || null },
      success: function(data) {
        updateFlight(data.sfid, data.points,
                     data.barogram_t, data.barogram_h,
                     data.enl, data.elevations);

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
 * Note: _lonlat, _levels, _time, _enl and _height MUST have the same number of
 *   elements when decoded.
 *
 * @param {int} tracking_id SkyLines tracking ID.
 * @param {String} _lonlat Google polyencoded string of geolocations
 *   (lon + lat, WSG 84).
 * @param {String} _time Google polyencoded string of time values.
 * @param {String} _height Google polyencoded string of height values.
 * @param {String} _enl Google polyencoded string of enl values.
 * @param {String} _elevations Google polyencoded string of elevations.
 */

function updateFlight(tracking_id, _lonlat, _time,
    _height, _enl, _elevations) {
  // find the flight to update
  var flight = flights.get(tracking_id);
  if (!flight)
    return;

  flight.update(_lonlat, _time, _height, _enl, _elevations);
  setTime(global_time);
}
