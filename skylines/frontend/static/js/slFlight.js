/**
 * A SkyLines flight.
 * @constructor
 * @param {Number} _sfid SkyLines flight ID.
 * @param {String} _lonlat Google polyencoded string of geolocations
 *   (lon + lat, WSG 84).
 * @param {String} _time Google polyencoded string of time values.
 * @param {String} _height Google polyencoded string of height values.
 * @param {String} _enl Google polyencoded string of engine noise levels.
 * @param {String} _elevations_t Google polyencoded string of elevation
 *   time values.
 * @param {String} _elevations_h Google polyencoded string of elevations.
 * @param {Number} _geoid Approximate geoid height at the takeoff location
 * @param {Object=} opt_additional May contain additional information about
 *   the flight, e.g. registration number, callsign, ...
 */
slFlight = function(_sfid, _lonlat, _time, _height, _enl,
                    _elevations_t, _elevations_h, _geoid,
                    opt_additional) {
  var flight = {};

  var time;
  var enl;
  var geometry;
  var color;
  var sfid = _sfid;
  var plane;
  var last_update;
  var elev_t = [];
  var elev_h = [];
  var flot_h = [];
  var flot_enl = [];
  var flot_elev = [];
  var additional = opt_additional || {};
  var geoid = _geoid;

  flight.init = function(_lonlat, _time, _height, _enl,
                         _elevations_t, _elevations_h) {
    var height = ol.format.Polyline.decodeDeltas(_height, 1, 1);
    time = ol.format.Polyline.decodeDeltas(_time, 1, 1);
    var enl = ol.format.Polyline.decodeDeltas(_enl, 1, 1);
    var lonlat = ol.format.Polyline.decodeDeltas(_lonlat, 2);

    geometry = new ol.geom.LineString([], 'XYZM');

    var lonlatLength = lonlat.length;
    for (var i = 0; i < lonlatLength; i += 2) {
      var point = ol.proj.transform([lonlat[i + 1], lonlat[i]],
                                    'EPSG:4326', 'EPSG:3857');
      geometry.appendCoordinate([point[0], point[1],
                                 height[i / 2] + geoid, time[i / 2]]);
    }

    var timeLength = time.length;
    for (var i = 0; i < timeLength; ++i) {
      var timestamp = time[i] * 1000;
      flot_h.push([timestamp, slUnits.convertAltitude(height[i])]);
      flot_enl.push([timestamp, enl[i]]);
    }

    // Add flight as a row to the fix data table
    //fix_table.addRow(sfid, color, _additional['competition_id']);

    var _elev_t = ol.format.Polyline.decodeDeltas(_elevations_t, 1, 1);
    var _elev_h = ol.format.Polyline.decodeDeltas(_elevations_h, 1, 1);

    for (var i = 0; i < _elev_t.length; i++) {
      var timestamp = _elev_t[i] * 1000;
      var e = _elev_h[i];
      if (e < -500)
        e = null;

      elev_t.push(_elev_t[i]);
      elev_h.push(e);
      flot_elev.push([timestamp, e ? slUnits.convertAltitude(e) : null]);
    }

    sfid = _sfid;
    plane = { point: null, marker: null };
    last_update = time[time.length - 1];
  };

  flight.update = function(_lonlat, _time,
                           _height, _enl, _elevations) {
    var height_decoded = ol.format.Polyline.decodeDeltas(_height, 1, 1);
    var time_decoded = ol.format.Polyline.decodeDeltas(_time, 1, 1);
    var enl_decoded = ol.format.Polyline.decodeDeltas(_enl, 1, 1);
    var lonlat = ol.format.Polyline.decodeDeltas(_lonlat, 2);
    var elev = ol.format.Polyline.decodeDeltas(_elevations, 1, 1);

    // we skip the first point in the list because we assume it's the "linking"
    // fix between the data we already have and the data to add.
    if (time_decoded.length < 2) return;

    var _flot_h = [], _flot_enl = [], _flot_elev = [],
        _elev_t = [], _elev_h = [];
    for (var i = 1; i < time_decoded.length; i++) {
      var timestamp = time_decoded[i] * 1000;

      var point = ol.proj.transform([lonlat[(i * 2) + 1], lonlat[i * 2]],
                                    'EPSG:4326', 'EPSG:3857');
      geometry.appendCoordinate([point[0], point[1],
                                 height_decoded[i], time_decoded[i]]);

      flot_h.push([timestamp, slUnits.convertAltitude(height_decoded[i])]);
      flot_enl.push([timestamp, enl_decoded[i]]);

      var e = elev[i];
      if (e < -500)
        e = null;

      elev_t.push(time_decoded[i]);
      elev_h.push(e);
      flot_elev.push([timestamp, e ? slUnits.convertAltitude(e) : null]);
    }

    time = time.concat(time_decoded);
    last_update = time_decoded[time_decoded.length - 1];
  };

  flight.setColor = function(_color) {
    color = _color;
  };

  flight.getColor = function() {
    return color;
  };

  flight.getGeometry = function() {
    return geometry;
  };

  flight.getCompetitionID = function() {
    if ('competition_id' in additional)
      return additional['competition_id'];
    else
      return undefined;
  };

  flight.getRegistration = function() {
    if ('registration' in additional)
      return additional['registration'];
    else
      return undefined;
  };

  flight.getStartTime = function() {
    return time[0];
  };

  flight.getEndTime = function() {
    return time[time.length - 1];
  };

  flight.getTime = function() {
    return time;
  };

  flight.getFlotElev = function() {
    return flot_elev;
  };

  flight.getFlotHeight = function() {
    return flot_h;
  };

  flight.getFlotENL = function() {
    return flot_enl;
  };

  flight.getFixData = function(t) {
    if (t == -1)
      t = flight.getEndTime();
    else if (t < flight.getStartTime() || t > flight.getEndTime())
      return null;

    var index = getNextSmallerIndex(time, t);
    if (index < 0 || index >= time.length - 1 ||
        time[index] == undefined || time[index + 1] == undefined)
      return null;

    var t_prev = time[index];
    var t_next = time[index + 1];
    var dt_total = t_next - t_prev;

    var fix_data = {};

    fix_data['time'] = t_prev;

    var _loc_prev = geometry.getCoordinateAtM(t_prev);
    var _loc_current = geometry.getCoordinateAtM(t);
    var _loc_next = geometry.getCoordinateAtM(t_next);

    fix_data['lon'] = _loc_current[0];
    fix_data['lat'] = _loc_current[1];

    fix_data['heading'] = Math.atan2(_loc_next[0] - _loc_prev[0],
                                     _loc_next[1] - _loc_prev[1]);

    fix_data['alt-msl'] = _loc_current[2] - geoid;

    var loc_prev = ol.proj.transform(_loc_prev, 'EPSG:3857', 'EPSG:4326');
    var loc_next = ol.proj.transform(_loc_next, 'EPSG:3857', 'EPSG:4326');

    if (dt_total != 0) {
      fix_data['speed'] = geographicDistance(loc_next, loc_prev) / dt_total;
      fix_data['vario'] = (_loc_next[2] - _loc_prev[2]) / dt_total;
    }

    if (elev_t !== undefined && elev_h !== undefined) {
      var elev_index = getNextSmallerIndex(elev_t, t);
      if (elev_index >= 0 && elev_index < elev_t.length) {
        var elev = elev_h[elev_index];
        if (elev) {
          fix_data['alt-gnd'] = fix_data['alt-msl'] - elev_h[elev_index];
          if (fix_data['alt-gnd'] < 0)
            fix_data['alt-gnd'] = 0;
        }
      }
    }

    return fix_data;
  };

  flight.getPlane = function() {
    return plane;
  };

  flight.getLastUpdate = function() {
    return last_update;
  };

  flight.getID = function() {
    return sfid;
  };

  flight.getGeoid = function() {
    return geoid;
  };

  flight.init(_lonlat, _time, _height, _enl,
              _elevations_t, _elevations_h);
  return flight;
};
