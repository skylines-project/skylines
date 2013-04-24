slUnits = (function() {
  var slUnits = {};

  /**
   * The list of supported unit types.
   * For each type the corresponding functions are generated dynamically.
   * @const
   * @type {Array}
   */
  var UNIT_TYPES = ['Distance', 'Speed', 'Lift', 'Altitude'];

  /**
   * The number of elements in the UNIT_TYPES array.
   * @const
   * @type {number}
   */
  var UNIT_TYPES_LENGTH = UNIT_TYPES.length;

  /**
   * A static dictionary of the supported units with its
   * conversion factors and default decimal places.
   * @const
   * @type {Object}
   */
  var UNITS = {
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
    'ft/min': [196.850394, 0]
  };

  /**
   * The container that saves the user unit settings
   * @type {Object}
   */
  var settings = {
    'Distance': 'm',
    'Speed': 'km/h',
    'Lift': 'm/s',
    'Altitude': 'm'
  };

  /**
   * Initialises the slUnits module with the user settings
   *
   * @param {String} distance The distance unit (e.g. 'km').
   * @param {String} speed The speed unit (e.g. 'km/h').
   * @param {String} lift The vertical speed unit (e.g. 'm/s').
   * @param {String} altitude The altitude unit (e.g. 'm').
   */
  slUnits.init = function(distance, speed, lift, altitude) {
    if (UNITS[distance]) settings['Distance'] = distance;
    if (UNITS[speed]) settings['Speed'] = speed;
    if (UNITS[lift]) settings['Lift'] = lift;
    if (UNITS[altitude]) settings['Altitude'] = altitude;
  };

  /**
   * Formats a number to a string with a given number of decimal places
   *
   * @param  {number} value A number that should be formatted.
   * @param  {[type]} decimals
   *   The number of decimal places that should be kept.
   * @return {String} The formatted value as a string.
   */
  slUnits.formatDecimal = function(value, decimals) {
    return value.toFixed(decimals);
  };

  function generateFunctions(unit_type) {
    // Generate e.g. formatDistance(value) functions
    slUnits['format' + unit_type] = function(value) {
      value = slUnits['convert' + unit_type](value);
      return slUnits['add' + unit_type + 'Unit'](value);
    };

    // Generate e.g. convertDistance(value) functions
    slUnits['convert' + unit_type] = function(value) {
      return value * UNITS[settings[unit_type]][0];
    };

    // Generate e.g. addDistanceUnit(value) functions
    slUnits['add' + unit_type + 'Unit'] = function(value) {
      value = slUnits.formatDecimal(value, UNITS[settings[unit_type]][1]);
      return value + ' ' + settings[unit_type];
    };
  }

  for (var i = 0; i < UNIT_TYPES_LENGTH; ++i) {
    generateFunctions(UNIT_TYPES[i]);
  }

  return slUnits;
})();
