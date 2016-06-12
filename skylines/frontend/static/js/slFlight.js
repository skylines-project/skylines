/**
 * A SkyLines flight.
 * @constructor
 * @param {Number} _sfid SkyLines flight ID.
 * @param {String} _lonlat Google polyencoded string of geolocations
 *   (lon + lat, WSG 84).
 * @param {String} _time Google polyencoded string of time values.
 * @param {String} _height Google polyencoded string of height values.
 * @param {String} _enl Google polyencoded string of engine noise levels.
 * @param {String} _elev_t Google polyencoded string of elevation
 *   time values.
 * @param {String} _elev_h Google polyencoded string of elevations.
 * @param {Number} _geoid Approximate geoid height at the takeoff location
 * @param {Object=} opt_additional May contain additional information about
 *   the flight, e.g. registration number, callsign, ...
 */
slFlight = Ember.Object.extend({
  color: null,
  last_update: Ember.computed.readOnly('time.lastObject'),

  startTime: Ember.computed.readOnly('time.firstObject'),
  endTime: Ember.computed.readOnly('time.lastObject'),

  init: function() {
    this.set('plane', { point: null, marker: null });
  },

  update: function(_lonlat, _time, _height, _enl, _elevations) {
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
      this.get('geometry').appendCoordinate([point[0], point[1],
                                 height_decoded[i], time_decoded[i]]);

      this.get('flot_h').push([timestamp, slUnits.convertAltitude(height_decoded[i])]);
      this.get('flot_enl').push([timestamp, enl_decoded[i]]);

      var e = elev[i];
      if (e < -500)
        e = null;

      this.get('elev_t').push(time_decoded[i]);
      this.get('elev_h').push(e);
      this.get('flot_elev').push([timestamp, e ? slUnits.convertAltitude(e) : null]);
    }

    this.set('time', this.get('time').concat(time_decoded));
  },

  getFixData: function(t) {
    if (t == -1)
      t = this.get('endTime');
    else if (t < this.get('startTime') || t > this.get('endTime'))
      return null;

    var time = this.get('time');
    var geometry = this.get('geometry');
    var geoid = this.get('geoid');

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

    var elev_t = this.get('elev_t');
    var elev_h = this.get('elev_h');
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
  },

  getID: function() {
    return this.get('id');
  }
});

slFlight.fromData = function(data) {
  var _lonlat = ol.format.Polyline.decodeDeltas(data.points, 2);
  var _time = ol.format.Polyline.decodeDeltas(data.barogram_t, 1, 1);
  var _height = ol.format.Polyline.decodeDeltas(data.barogram_h, 1, 1);
  var _enl = ol.format.Polyline.decodeDeltas(data.enl, 1, 1);
  var _elev_t = ol.format.Polyline.decodeDeltas(data.elevations_t, 1, 1);
  var _elev_h = ol.format.Polyline.decodeDeltas(data.elevations_h, 1, 1);

  var geometry = new ol.geom.LineString([], 'XYZM');
  for (var i = 0, len = _lonlat.length; i < len; i += 2) {
    var point = ol.proj.transform([_lonlat[i + 1], _lonlat[i]], 'EPSG:4326', 'EPSG:3857');
    geometry.appendCoordinate([point[0], point[1], _height[i / 2] + data.geoid, _time[i / 2]]);
  }

  var flot_h = [];
  var flot_enl = [];
  for (var i = 0, len = _time.length; i < len; ++i) {
    var timestamp = _time[i] * 1000;
    flot_h.push([timestamp, slUnits.convertAltitude(_height[i])]);
    flot_enl.push([timestamp, _enl[i]]);
  }

  var elev_t = [];
  var elev_h = [];
  var flot_elev = [];
  for (var i = 0, len = _elev_t.length; i < len; i++) {
    var timestamp = _elev_t[i] * 1000;
    var e = _elev_h[i];
    if (e < -500)
      e = null;

    elev_t.push(_elev_t[i]);
    elev_h.push(e);
    flot_elev.push([timestamp, e ? slUnits.convertAltitude(e) : null]);
  }

  var additional = data.additional || {};

  return slFlight.create({
    id: data.sfid,
    geometry: geometry,
    time: _time,
    flot_h: flot_h,
    flot_enl: flot_enl,
    elev_t: elev_t,
    elev_h: elev_h,
    flot_elev: flot_elev,
    geoid: data.geoid,
    competition_id: additional.competition_id,
    registration: additional.registration
  });
};
