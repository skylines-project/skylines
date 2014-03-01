

/**
 * Retrieves all new traces for the displayed flights
 */
function updateFlightsFromJSON() {
  flights.each(function(flight) {
    var url = '/tracking/' + flight.sfid + '/json';

    $.ajax(url, {
      data: { last_update: flight.last_update || null },
      success: function(data) {
        updateFlight(data.sfid, data.encoded.points, data.encoded.levels,
                     data.num_levels, data.barogram_t, data.barogram_h,
                     data.enl, data.elevations);

        initRedrawLayer(map.getLayersByName('Flight')[0]);
        updateBaroScale();
        updateBaroData();
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
 * @param {String} _levels Google polyencoded string of levels of detail.
 * @param {int} _num_levels Number of levels encoded in _lonlat and _levels.
 * @param {String} _time Google polyencoded string of time values.
 * @param {String} _height Google polyencoded string of height values.
 * @param {String} _enl Google polyencoded string of enl values.
 * @param {String} _elevations Google polyencoded string of elevations.
 */

function updateFlight(tracking_id, _lonlat, _levels, _num_levels, _time,
    _height, _enl, _elevations) {
  var polyline_decoder = new OpenLayers.Format.EncodedPolyline();

  var height = polyline_decoder.decodeDeltas(_height, 1, 1);
  var time = polyline_decoder.decodeDeltas(_time, 1, 1);
  var enl = polyline_decoder.decodeDeltas(_enl, 1, 1);
  var lonlat = polyline_decoder.decode(_lonlat, 2);
  var lod = polyline_decoder.decodeUnsignedIntegers(_levels);
  var elev = polyline_decoder.decodeDeltas(_elevations, 1, 1);

  // we skip the first point in the list because we assume it's the "linking"
  // fix between the data we already have and the data to add.

  if (lonlat.length < 2) return;

  var points = new Array();
  for (var i = 1, len = lonlat.length; i < len; i++) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i][1], lonlat[i][0]).
        transform(new OpenLayers.Projection('EPSG:4326'),
                  map.getProjectionObject()));
  }

  // find the flight to update
  var flight = flights.get(tracking_id);
  if (!flight)
    return;

  var flot_h = [], flot_enl = [], flot_elev = [], elev_t = [], elev_h = [];
  for (var i = 0; i < time.length; i++) {
    var timestamp = time[i] * 1000;
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
  flight.geo.components = flight.geo.components.concat(points);
  flight.geo.componentsLevel = flight.geo.componentsLevel.concat(lod.slice(1));
  flight.t = flight.t.concat(time.slice(1));
  flight.h = flight.h.concat(height.slice(1));
  flight.enl = flight.enl.concat(enl.slice(1));
  flight.elev_t = flight.elev_t.concat(elev_t.slice(1));
  flight.elev_h = flight.elev_h.concat(elev_h.slice(1));
  flight.lonlat = flight.lonlat.concat(lonlat.slice(1));
  flight.flot_h = flight.flot_h.concat(flot_h.slice(1));
  flight.flot_enl = flight.flot_enl.concat(flot_enl.slice(1));
  flight.flot_elev = flight.flot_elev.concat(flot_elev.slice(1));

  // recalculate bounds
  flight.geo.bounds = flight.geo.calculateBounds();
  // reset indices
  for (var i = 0, len = flight.geo.components.length; i < len; i++) {
    flight.geo.components[i].originalIndex = i;
  }

  flight.last_update = flight.t[flight.t.length - 1];

  setTime(global_time);
}
