

/**
 * Retrieves all new traces for the displayed flights
 */
function updateFlightsFromJSON() {
  flights.each(function(flight) {
    var url = '/tracking/' + flight.sfid + '/json';

    $.ajax(url, {
      data: { last_update: flight.last_update || null },
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

  var height = ol.format.Polyline.decodeDeltas(_height, 1, 1);
  var time = ol.format.Polyline.decodeDeltas(_time, 1, 1);
  var enl = ol.format.Polyline.decodeDeltas(_enl, 1, 1);
  var lonlat = ol.format.Polyline.decodeDeltas(_lonlat, 2);
  var elev = ol.format.Polyline.decodeDeltas(_elevations, 1, 1);

  // we skip the first point in the list because we assume it's the "linking"
  // fix between the data we already have and the data to add.
  if (time.length < 2) return;

  // find the flight to update
  var flight = flights.get(tracking_id);
  if (!flight)
    return;

  var flot_h = [], flot_enl = [], flot_elev = [], elev_t = [], elev_h = [];
  for (var i = 1; i < time.length; i++) {
    var timestamp = time[i] * 1000;

    var point = ol.proj.transform([lonlat[(i * 2) + 1], lonlat[i * 2]],
                                  'EPSG:4326', 'EPSG:3857');
    flight.geo.appendCoordinate([point[0], point[1], height[i], time[i]]);

    flot_h.push([timestamp, slUnits.convertAltitude(height[i])]);
    flot_enl.push([timestamp, enl[i]]);

    var e = elev[i];
    if (e < -500)
      e = null;

    elev_t.push(time[i]);
    elev_h.push(e);
    flot_elev.push([timestamp, e ? slUnits.convertAltitude(e) : null]);
  }

  // points is already sliced
  flight.t = flight.t.concat(time);
  flight.enl = flight.enl.concat(enl);
  flight.elev_t = flight.elev_t.concat(elev_t);
  flight.elev_h = flight.elev_h.concat(elev_h);
  flight.flot_h = flight.flot_h.concat(flot_h);
  flight.flot_enl = flight.flot_enl.concat(flot_enl);
  flight.flot_elev = flight.flot_elev.concat(flot_elev);

  flight.last_update = flight.t[flight.t.length - 1];

  setTime(global_time);
}
