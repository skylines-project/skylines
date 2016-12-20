import Ember from 'ember';
import ol from 'openlayers';

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
export default Ember.Object.extend({
  units: null,

  fixes: [],
  elevations: [],

  time: Ember.computed.map('fixes', fix => fix.time),

  coordinates: Ember.computed.map('fixes', function(fix) {
    let coordinate = [fix.latitude, fix.longitude, fix.altitude, fix.time];
    return ol.proj.transform(coordinate, 'EPSG:4326', 'EPSG:3857');
  }),

  flot_h: Ember.computed.map('fixes', function(fix) {
    return [fix.time * 1000, this.get('units').convertAltitude(fix.altitude)];
  }),

  flot_enl: Ember.computed.map('fixes', function(fix) {
    return [fix.time * 1000, fix.enl];
  }),

  elev_t: Ember.computed.map('elevations', it => it.time),
  elev_h: Ember.computed.map('elevations', it => it.elevation),

  flot_elev: Ember.computed.map('elevations', function(it) {
    return [it.time * 1000, it.elevation ? this.get('units').convertAltitude(it.elevation) : null];
  }),

  color: null,
  last_update: Ember.computed.readOnly('time.lastObject'),

  startTime: Ember.computed.readOnly('time.firstObject'),
  endTime: Ember.computed.readOnly('time.lastObject'),

  coordinatesObserver: Ember.observer('coordinates', function() {
    let coordinates = this.get('coordinates');
    this.get('geometry').setCoordinates(coordinates, 'XYZM');
  }),

  model: null,

  init() {
    this._super(...arguments);
    this.set('geometry', new ol.geom.LineString(this.get('coordinates'), 'XYZM'));
  },
});
