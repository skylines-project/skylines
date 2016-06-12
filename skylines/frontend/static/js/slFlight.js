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
      return Fix.create({ flight: this });

    var time = this.get('time');
    var geometry = this.get('geometry');
    var geoid = this.get('geoid');

    var index = getNextSmallerIndex(time, t);
    if (index < 0 || index >= time.length - 1 ||
        time[index] == undefined || time[index + 1] == undefined)
      return Fix.create({ flight: this });

    var t_prev = time[index];
    var t_next = time[index + 1];

    var fix_data = { flight: this, t: t, t_prev: t_prev, t_next: t_next };

    return Fix.create(fix_data);
  },

  getID: function() {
    return this.get('id');
  }
});

var Fix = Ember.Object.extend({
  time: Ember.computed.readOnly('t_prev'),

  coordinate: Ember.computed('flight.geometry', 't', function() {
    var t = this.get('t');
    if (!Ember.isNone(t)) {
      return this.get('flight.geometry').getCoordinateAtM(t);
    }
  }),

  lon: Ember.computed.readOnly('coordinate.0'),
  lat: Ember.computed.readOnly('coordinate.1'),

  'alt-msl': Ember.computed('coordinate.2', 'flight.geoid', function() {
    var altitude = this.get('coordinate.2');
    if (!Ember.isNone(altitude)) {
      return altitude - this.get('flight.geoid');
    }
  }),

  'alt-gnd': Ember.computed('alt-msl', 'elevation', function() {
    var altitude = this.get('alt-msl');
    var elevation = this.get('elevation');
    if (!Ember.isNone(altitude) && !Ember.isNone(elevation)) {
      var value = altitude - elevation;
      return (value >= 0) ? value : 0;
    }
  }),

  point: Ember.computed('coordinate', function() {
    var coordinate = this.get('coordinate');
    if (coordinate) {
      return new ol.geom.Point(coordinate);
    }
  }),

  heading: Ember.computed('_coordinate_prev', '_coordinate_next', function() {
    var prev = this.get('_coordinate_prev');
    var next = this.get('_coordinate_next');

    if (prev && next) {
      return Math.atan2(next[0] - prev[0], next[1] - prev[1]);
    }
  }),

  vario: Ember.computed('_coordinate_prev.2', '_coordinate_next.2', '_dt', function() {
    var prev = this.get('_coordinate_prev');
    var next = this.get('_coordinate_next');
    var dt = this.get('_dt');

    if (prev && next && dt) {
      return (next[2] - prev[2]) / dt;
    }
  }),

  speed: Ember.computed('_coordinate_prev', '_coordinate_next', '_dt', function() {
    var prev = this.get('_coordinate_prev');
    var next = this.get('_coordinate_next');
    var dt = this.get('_dt');

    if (prev && next && dt) {
      var loc_prev = ol.proj.transform(prev, 'EPSG:3857', 'EPSG:4326');
      var loc_next = ol.proj.transform(next, 'EPSG:3857', 'EPSG:4326');

      return geographicDistance(loc_next, loc_prev) / dt;
    }
  }),

  _dt: Ember.computed('t_prev', 't_next', function() {
    return this.get('t_next') - this.get('t_prev');
  }),

  _coordinate_prev: Ember.computed('flight.geometry', 't_prev', function() {
    return this.get('flight.geometry').getCoordinateAtM(this.get('t_prev'));
  }),

  _coordinate_next: Ember.computed('flight.geometry', 't_next', function() {
    return this.get('flight.geometry').getCoordinateAtM(this.get('t_next'));
  }),

  elevation: Ember.computed('flight.elev_h.[]', '_elev_index', function() {
    var elev_h = this.get('flight.elev_h');
    if (elev_h) {
      return elev_h[this.get('_elev_index')];
    }
  }),

  _elev_index: Ember.computed('flight.elev_t.[]', 't', function() {
    var elev_t = this.get('flight.elev_t');
    if (elev_t) {
      return getNextSmallerIndex(elev_t, this.get('t'));
    }
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
