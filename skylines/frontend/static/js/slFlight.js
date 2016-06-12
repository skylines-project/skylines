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
  fixes: [],
  elevations: [],

  time: Ember.computed.mapBy('fixes', 'time'),

  coordinates: Ember.computed.map('fixes', function(fix) {
    var coordinate = [fix.latitude, fix.longitude, fix.altitude, fix.time];
    return ol.proj.transform(coordinate, 'EPSG:4326', 'EPSG:3857');
  }),

  flot_h: Ember.computed.map('fixes', function(fix) {
    return [fix.time * 1000, slUnits.convertAltitude(fix.altitude)];
  }),

  flot_enl: Ember.computed.map('fixes', function(fix) {
    return [fix.time * 1000, fix.enl];
  }),

  elev_t: Ember.computed.mapBy('elevations', 'time'),
  elev_h: Ember.computed.mapBy('elevations', 'elevation'),

  flot_elev: Ember.computed.map('elevations', function(it) {
    return [it.time * 1000, it.elevation ? slUnits.convertAltitude(it.elevation) : null];
  }),

  color: null,
  last_update: Ember.computed.readOnly('time.lastObject'),

  startTime: Ember.computed.readOnly('time.firstObject'),
  endTime: Ember.computed.readOnly('time.lastObject'),

  coordinatesObserver: Ember.observer('coordinates', function() {
    var coordinates = this.get('coordinates');
    this.get('geometry').setCoordinates(coordinates, 'XYZM')
  }),

  init: function() {
    this.set('geometry', new ol.geom.LineString(this.get('coordinates'), 'XYZM'));
    this.set('plane', { point: null, marker: null });
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

    return Fix.create(fix_data);
  },

  getID: function() {
    return this.get('id');
  }
});

var Fix = Ember.Object.extend({
  coordinate: Ember.computed.collect('lon', 'lat'),

  point: Ember.computed('coordinate', function() {
    return new ol.geom.Point(this.get('coordinate'));
  })
});

slFlight.fromData = function(data) {
  var _time = ol.format.Polyline.decodeDeltas(data.barogram_t, 1, 1);
  var _lonlat = ol.format.Polyline.decodeDeltas(data.points, 2);
  var _height = ol.format.Polyline.decodeDeltas(data.barogram_h, 1, 1);
  var _enl = ol.format.Polyline.decodeDeltas(data.enl, 1, 1);

  var fixes = _time.map(function(timestamp, i) {
    return {
      time: timestamp,
      longitude: _lonlat[i * 2],
      latitude: _lonlat[i * 2 + 1],
      altitude: _height[i] + data.geoid,
      enl: _enl[i]
    };
  });

  var _elev_t = ol.format.Polyline.decodeDeltas(data.elevations_t, 1, 1);
  var _elev_h = ol.format.Polyline.decodeDeltas(data.elevations_h, 1, 1);

  var elevations = _elev_t.map(function(timestamp, i) {
    var elevation = _elev_h[i];

    return {
      time: timestamp,
      elevation: (elevation > -500) ? elevation : null
    }
  });

  var additional = data.additional || {};

  return slFlight.create({
    id: data.sfid,
    fixes: fixes,
    elevations: elevations,
    geoid: data.geoid,
    competition_id: additional.competition_id,
    registration: additional.registration
  });
};
