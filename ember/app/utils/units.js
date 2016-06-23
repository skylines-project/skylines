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
export function init(distance, speed, lift, altitude) {
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

export function formatDistance(value) {
  value = convertDistance(value);
  return addDistanceUnit(value);
}

export function convertDistance(value) {
  return value * UNITS[settings['Distance']][0];
}

export function addDistanceUnit(value) {
  value = formatDecimal(value, UNITS[settings['Distance']][1]);
  return value + ' ' + settings['Distance'];
}

export function getDistanceUnit() {
  return settings['Distance'];
}

export function formatSpeed(value) {
  value = convertSpeed(value);
  return addSpeedUnit(value);
}

export function convertSpeed(value) {
  return value * UNITS[settings['Speed']][0];
}

export function addSpeedUnit(value) {
  value = formatDecimal(value, UNITS[settings['Speed']][1]);
  return value + ' ' + settings['Speed'];
}

export function getSpeedUnit() {
  return settings['Speed'];
}

export function formatLift(value) {
  value = convertLift(value);
  return addLiftUnit(value);
}

export function convertLift(value) {
  return value * UNITS[settings['Lift']][0];
}

export function addLiftUnit(value) {
  value = formatDecimal(value, UNITS[settings['Lift']][1]);
  return value + ' ' + settings['Lift'];
}

export function getLiftUnit() {
  return settings['Lift'];
}

export function formatAltitude(value) {
  value = convertAltitude(value);
  return addAltitudeUnit(value);
}

export function convertAltitude(value) {
  return value * UNITS[settings['Altitude']][0];
}

export function addAltitudeUnit(value) {
  value = formatDecimal(value, UNITS[settings['Altitude']][1]);
  return value + ' ' + settings['Altitude'];
}

export function getAltitudeUnit() {
  return settings['Altitude'];
}
