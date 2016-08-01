import Ember from 'ember';

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
  'km': [1 / 1000., 0],
  'NM': [1 / 1852., 0],
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

/**
 * The container that saves the user unit settings
 * @type {Object}
 */
let settings = {
  'Distance': 'km',
  'Speed': 'km/h',
  'Lift': 'm/s',
  'Altitude': 'm',
};

/**
 * Initialises the module with the user settings
 *
 * @param {String} distance The distance unit (e.g. 'km').
 * @param {String} speed The speed unit (e.g. 'km/h').
 * @param {String} lift The vertical speed unit (e.g. 'm/s').
 * @param {String} altitude The altitude unit (e.g. 'm').
 */
function init(distance, speed, lift, altitude) {
  if (UNITS[distance]) {
    settings['Distance'] = distance;
  }
  if (UNITS[speed]) {
    settings['Speed'] = speed;
  }
  if (UNITS[lift]) {
    settings['Lift'] = lift;
  }
  if (UNITS[altitude]) {
    settings['Altitude'] = altitude;
  }
}

/**
 * Formats a number to a string with a given number of decimal places
 *
 * @param  {Number} value A number that should be formatted.
 * @param  {Number} decimals
 *   The number of decimal places that should be kept.
 * @return {String} The formatted value as a string.
 */
export function formatDecimal(value, decimals) {
  return value.toFixed(decimals);
}

export function formatDistance(value, options) {
  value = convertDistance(value);
  return addDistanceUnit(value, options);
}

export function convertDistance(value) {
  return value * UNITS[settings['Distance']][0];
}

export function addDistanceUnit(value, options = {}) {
  let decimals = (options.decimals !== undefined) ? options.decimals : UNITS[settings['Distance']][1];
  value = formatDecimal(value, decimals);
  return (options.withUnit !== false) ? `${value} ${settings['Distance']}` : value;
}

export function getDistanceUnit() {
  return settings['Distance'];
}

export function formatSpeed(value, options) {
  value = convertSpeed(value);
  return addSpeedUnit(value, options);
}

export function convertSpeed(value) {
  return value * UNITS[settings['Speed']][0];
}

export function addSpeedUnit(value, options = {}) {
  let decimals = (options.decimals !== undefined) ? options.decimals : UNITS[settings['Speed']][1];
  value = formatDecimal(value, decimals);
  return (options.withUnit !== false) ? `${value} ${settings['Speed']}` : value;
}

export function getSpeedUnit() {
  return settings['Speed'];
}

export function formatLift(value, options) {
  value = convertLift(value);
  return addLiftUnit(value, options);
}

export function convertLift(value) {
  return value * UNITS[settings['Lift']][0];
}

export function addLiftUnit(value, options = {}) {
  let decimals = (options.decimals !== undefined) ? options.decimals : UNITS[settings['Lift']][1];
  value = formatDecimal(value, decimals);
  return (options.withUnit !== false) ? `${value} ${settings['Lift']}` : value;
}

export function getLiftUnit() {
  return settings['Lift'];
}

export function formatAltitude(value, options) {
  value = convertAltitude(value);
  return addAltitudeUnit(value, options);
}

export function convertAltitude(value) {
  return value * UNITS[settings['Altitude']][0];
}

export function addAltitudeUnit(value, options = {}) {
  let decimals = (options.decimals !== undefined) ? options.decimals : UNITS[settings['Altitude']][1];
  value = formatDecimal(value, decimals);
  return (options.withUnit !== false) ? `${value} ${settings['Altitude']}` : value;
}

export function getAltitudeUnit() {
  return settings['Altitude'];
}

init(
  Ember.$('meta[name=skylines-distance-unit]').attr('content'),
  Ember.$('meta[name=skylines-speed-unit]').attr('content'),
  Ember.$('meta[name=skylines-lift-unit]').attr('content'),
  Ember.$('meta[name=skylines-altitude-unit]').attr('content')
);
