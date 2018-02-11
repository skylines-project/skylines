import { computed } from '@ember/object';
import Service, { inject as service } from '@ember/service';

/**
 * A static dictionary of the supported units with its
 * conversion factors and default decimal places.
 * @const
 * @type {Object}
 */
const UNITS = {
  // Length
  'm': [1, 0],
  'ft': [3.28084, 0],
  'km': [1 / 1000.0, 0],
  'NM': [1 / 1852.0, 0],
  'mi': [1 / 1609.34, 0],

  // Speed
  'm/s': [1, 1],
  'km/h': [3.6, 1],
  'kt': [1.94384449, 1],
  'mph': [2.23693629, 1],
  'ft/min': [196.850394, 0],
};

export const PRESETS = {
  'european': {
    'distance': 'km',
    'speed': 'km/h',
    'lift': 'm/s',
    'altitude': 'm',
  },

  'british': {
    'distance': 'km',
    'speed': 'kt',
    'lift': 'kt',
    'altitude': 'ft',
  },

  'australian': {
    'distance': 'km',
    'speed': 'km/h',
    'lift': 'kt',
    'altitude': 'ft',
  },

  'american': {
    'distance': 'mi',
    'speed': 'kt',
    'lift': 'kt',
    'altitude': 'ft',
  },
};

export default Service.extend({
  intl: service(),

  distanceUnitIndex: 1,
  speedUnitIndex: 1,
  liftUnitIndex: 0,
  altitudeUnitIndex: 0,

  distanceUnit: computedUnit('distanceUnits', 'distanceUnitIndex'),
  speedUnit: computedUnit('speedUnits', 'speedUnitIndex'),
  liftUnit: computedUnit('liftUnits', 'liftUnitIndex'),
  altitudeUnit: computedUnit('altitudeUnits', 'altitudeUnitIndex'),

  distanceUnits: ['m', 'km', 'NM', 'mi'],
  speedUnits: ['m/s', 'km/h', 'kt', 'mph'],
  liftUnits: ['m/s', 'kt', 'ft/min'],
  altitudeUnits: ['m', 'ft'],

  /**
   * Formats a number to a string with a given number of decimal places
   *
   * @param  {Number} value A number that should be formatted.
   * @param  {Number} decimals
   *   The number of decimal places that should be kept.
   * @return {String} The formatted value as a string.
   */
  formatDecimal(value, decimals) {
    return this.get('intl').formatNumber(value, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  },

  formatDistance(value, options) {
    value = this.convertDistance(value);
    return this.addDistanceUnit(value, options);
  },

  convertDistance(value) {
    return value * UNITS[this.get('distanceUnit')][0];
  },

  addDistanceUnit(value, options = {}) {
    let decimals = (options.decimals !== undefined) ? options.decimals : UNITS[this.get('distanceUnit')][1];
    value = this.formatDecimal(value, decimals);
    return (options.withUnit !== false) ? `${value} ${this.get('distanceUnit')}` : value;
  },

  formatSpeed(value, options) {
    value = this.convertSpeed(value);
    return this.addSpeedUnit(value, options);
  },

  convertSpeed(value) {
    return value * UNITS[this.get('speedUnit')][0];
  },

  addSpeedUnit(value, options = {}) {
    let decimals = (options.decimals !== undefined) ? options.decimals : UNITS[this.get('speedUnit')][1];
    value = this.formatDecimal(value, decimals);
    return (options.withUnit !== false) ? `${value} ${this.get('speedUnit')}` : value;
  },

  formatLift(value, options) {
    value = this.convertLift(value);
    return this.addLiftUnit(value, options);
  },

  convertLift(value) {
    return value * UNITS[this.get('liftUnit')][0];
  },

  addLiftUnit(value, options = {}) {
    let decimals = (options.decimals !== undefined) ? options.decimals : UNITS[this.get('liftUnit')][1];
    value = this.formatDecimal(value, decimals);
    return (options.withUnit !== false) ? `${value} ${this.get('liftUnit')}` : value;
  },

  formatAltitude(value, options) {
    value = this.convertAltitude(value);
    return this.addAltitudeUnit(value, options);
  },

  convertAltitude(value) {
    return value * UNITS[this.get('altitudeUnit')][0];
  },

  addAltitudeUnit(value, options = {}) {
    let decimals = (options.decimals !== undefined) ? options.decimals : UNITS[this.get('altitudeUnit')][1];
    value = this.formatDecimal(value, decimals);
    return (options.withUnit !== false) ? `${value} ${this.get('altitudeUnit')}` : value;
  },
});

function computedUnit(unitsKey, indexKey) {
  return computed(indexKey, {
    get() {
      return this.get(unitsKey)[this.get(indexKey)];
    },
    set(key, value) {
      this.set(indexKey, this.get(unitsKey).indexOf(value));
      return value;
    },
  });
}
