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
var slFlight = Backbone.Model.extend({
  // Set the id attribute to sfid
  idAttribute: 'sfid',

  // Default attributes of the flight
  defaults: function() {
    return {
      time: null,
      enl: null,
      geometry: new ol.geom.LineString([], 'XYZM'),
      color: null,
      sfid: null,
      plane: { point: null, marker: null },
      last_update: null,
      elev_t: [],
      elev_h: [],
      flot_h: [],
      flot_enl: [],
      flot_elev: [],
      additional: {},
      geoid: null,
      selected: false
    };
  },

  parse: function(data) {
    if ('last_update' in this.attributes) {
      var attrs = this.attributes;
      var start = 1;
    } else {
      var attrs = this.defaults();
      var start = 0;
    }

    if ('geoid' in data)
      attrs.geoid = data.geoid;
    else
      attrs.geoid = 0;

    var time_decoded = ol.format.Polyline.decodeDeltas(data.barogram_t, 1, 1);

    // we skip the first point in the list because we assume it's the "linking"
    // fix between the data we already have and the data to add.
    if (time_decoded.length < 2) return;

    if (attrs.last_update == null) {
      attrs.time = time_decoded;
    } else {
      attrs.time = attrs.time.concat(time_decoded);
    }

    var height = ol.format.Polyline.decodeDeltas(data.barogram_h, 1, 1);
    var enl = ol.format.Polyline.decodeDeltas(data.enl, 1, 1);
    var lonlat = ol.format.Polyline.decodeDeltas(data.points, 2);

    var lonlatLength = lonlat.length;
    for (var i = start * 2; i < lonlatLength; i += 2) {
      var point = ol.proj.transform([lonlat[i + 1], lonlat[i]],
                                    'EPSG:4326', 'EPSG:3857');
      attrs.geometry.appendCoordinate([point[0],
                                       point[1],
                                       height[i / 2] + attrs.geoid,
                                       time_decoded[i / 2]]);
    }

    var timeLength = time_decoded.length;
    for (var i = start; i < timeLength; ++i) {
      var timestamp = time_decoded[i] * 1000;
      attrs.flot_h.push([timestamp, slUnits.convertAltitude(height[i])]);
      attrs.flot_enl.push([timestamp, enl[i]]);
    }

    if ('elevations_t' in data)
      var _elev_t = ol.format.Polyline.decodeDeltas(data.elevations_t, 1, 1);
    else
      var _elev_t = time_decoded;

    if ('elevations_h' in data)
      var _elev_h = ol.format.Polyline.decodeDeltas(data.elevations_h, 1, 1);
    else
      var _elev_h = ol.format.Polyline.decodeDeltas(data.elevations, 1, 1);

    for (var i = start; i < _elev_t.length; i++) {
      var timestamp = _elev_t[i] * 1000;
      var e = _elev_h[i];
      if (e < -500)
        e = null;

      attrs.elev_t.push(_elev_t[i]);
      attrs.elev_h.push(e);
      attrs.flot_elev.push([timestamp, e ? slUnits.convertAltitude(e) : null]);
    }

    attrs.id = data.sfid;
    attrs.sfid = data.sfid;
    attrs.last_update = attrs.time[attrs.time.length - 1];

    if ('additional' in data)
      attrs.additional = data.additional;

    return attrs;
  },

  url: function() {
    // this is appended to collection.url() which
    // returns collection.urlRoot + model.id
    return 'json';
  },

  update: function() {
    this.fetch({data: {last_update: this.attributes.last_update}});
  },

  setColor: function(_color) {
    this.attributes.color = _color;
  },

  getColor: function() {
    return this.attributes.color;
  },

  getGeometry: function() {
    return this.attributes.geometry;
  },

  getCompetitionID: function() {
    if ('competition_id' in this.attributes.additional)
      return this.attributes.additional['competition_id'];
    else
      return undefined;
  },

  getRegistration: function() {
    if ('registration' in this.attributes.additional)
      return this.attributes.additional['registration'];
    else
      return undefined;
  },

  getStartTime: function() {
    return this.attributes.time[0];
  },

  getEndTime: function() {
    return this.attributes.time[this.attributes.time.length - 1];
  },

  getTime: function() {
    return this.attributes.time;
  },

  getFlotElev: function() {
    return this.attributes.flot_elev;
  },

  getFlotHeight: function() {
    return this.attributes.flot_h;
  },

  getFlotENL: function() {
    return this.attributes.flot_enl;
  },

  getFixData: function(t) {
    if (t == -1)
      t = this.getEndTime();
    else if (t < this.getStartTime() || t > this.getEndTime())
      return null;

    var index = getNextSmallerIndex(this.attributes.time, t);
    if (index < 0 || index >= this.attributes.time.length - 1 ||
        this.attributes.time[index] == undefined ||
        this.attributes.time[index + 1] == undefined)
      return null;

    var t_prev = this.attributes.time[index];
    var t_next = this.attributes.time[index + 1];
    var dt_total = t_next - t_prev;

    var fix_data = {};

    fix_data['time'] = t_prev;

    var _loc_prev = this.attributes.geometry.getCoordinateAtM(t_prev);
    var _loc_current = this.attributes.geometry.getCoordinateAtM(t);
    var _loc_next = this.attributes.geometry.getCoordinateAtM(t_next);

    fix_data['lon'] = _loc_current[0];
    fix_data['lat'] = _loc_current[1];

    fix_data['heading'] = Math.atan2(_loc_next[0] - _loc_prev[0],
                                     _loc_next[1] - _loc_prev[1]);

    fix_data['alt-msl'] = _loc_current[2] - this.attributes.geoid;

    var loc_prev = ol.proj.transform(_loc_prev, 'EPSG:3857', 'EPSG:4326');
    var loc_next = ol.proj.transform(_loc_next, 'EPSG:3857', 'EPSG:4326');

    if (dt_total != 0) {
      fix_data['speed'] = geographicDistance(loc_next, loc_prev) / dt_total;
      fix_data['vario'] = (_loc_next[2] - _loc_prev[2]) / dt_total;
    }

    if (this.attributes.elev_t !== undefined &&
        this.attributes.elev_h !== undefined) {
      var elev_index = getNextSmallerIndex(this.attributes.elev_t, t);
      if (elev_index >= 0 && elev_index < this.attributes.elev_t.length) {
        var elev = this.attributes.elev_h[elev_index];
        if (elev) {
          fix_data['alt-gnd'] = fix_data['alt-msl'] -
                                this.attributes.elev_h[elev_index];
          if (fix_data['alt-gnd'] < 0)
            fix_data['alt-gnd'] = 0;
        }
      }
    }

    return fix_data;
  },

  getPlane: function() {
    return this.attributes.plane;
  },

  getLastUpdate: function() {
    return this.attributes.last_update;
  },

  getID: function() {
    return this.attributes.sfid;
  },

  getGeoid: function() {
    return this.attributes.geoid;
  },

  toggleSelection: function(value) {
    this.attributes.selected = !this.attributes.selected;
  },

  getSelection: function() {
    return this.attributes.selected;
  }
});
