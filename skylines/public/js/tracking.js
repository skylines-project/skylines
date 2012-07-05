/**
 * Function: updateFlightsFromJSON
 *
 * Retrieves all new traces for the displayed flights
 */
function updateFlightsFromJSON() {
  for (fid in flights) {
    var url = "/tracking/" + flights[fid].sfid + "/json";

    $.ajax(url, {
      success: function(data) {
        updateFlight(data.sfid, data.encoded.points, data.encoded.levels,
                     data.num_levels, data.barogram_t, data.barogram_h);

        map.events.triggerEvent("move");
        $.proxy(updateBarogram, { reset_y_axis: true })();
      }
    });
  }
};

/**
 * Function: updateFlight
 *
 * Updates a tracking flight.
 *
 * Parameters:
 * tracking_id - {int} SkyLines tracking ID
 * _lonlat - {String} Google polyencoded string of geolocations (lon + lat, WSG 84)
 * _levels - {String} Google polyencoded string of levels of detail
 * _num_levels - {int} Number of levels encoded in _lonlat and _levels
 * _time - {String} Google polyencoded string of time values
 * _height - {String} Google polyencoded string of height values
 *
 * Note: _lonlat, _levels, _time and _height MUST have the same number of elements when decoded.
 */

function updateFlight(tracking_id, _lonlat, _levels, _num_levels, _time, _height) {
  var height = OpenLayers.Util.decodeGoogle(_height);
  var time = OpenLayers.Util.decodeGoogle(_time);
  var lonlat = OpenLayers.Util.decodeGooglePolyline(_lonlat);
  var lod = OpenLayers.Util.decodeGoogleLoD(_levels, _num_levels);

  var points = new Array();
  for (var i = 0, len = lonlat.length; i < len; i++) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i].lon, lonlat[i].lat).
      transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()) );
  }

  // find the flight to update
  var update = -1;
  for (fid in flights) {
    if (tracking_id == flights[fid].sfid)
      update = fid;
  }

  if (update == -1) return;

  // update flight
  var flight = flights[update];

  flight.geo.components = points;
  flight.geo.componentsLevel = lod;
  flight.t = time;
  flight.h = height;
  flight.lonlat = lonlat;
  // recalculate bounds
  flight.geo.bounds = flight.geo.calculateBounds();
  // reset indices
  for (var i = 0, len = flight.geo.components.length; i < len; i++) {
    flight.geo.components[i].originalIndex = i;
  }

  barogram_t[fid] = time;
  barogram_h[fid] = height;
};
