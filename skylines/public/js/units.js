(function() {
  slUnits = new function() {
    var slUnits = this;

    /**
     * Formats a number to a string with a given number of decimal places
     *
     * @param  {number} value A number that should be formatted.
     * @param  {[type]} decimals
     *   The number of decimal places that should be kept.
     * @return {String} The formatted value as a string.
     */
    slUnits.format_decimal = function(value, decimals) {
      return value.toFixed(decimals);
    };

    var UNIT_TYPES = ['distance', 'speed', 'lift', 'altitude'];
    var UNIT_TYPES_LENGTH = UNIT_TYPES.length;

    /**
     * The container that saves the user unit settings
     * @type {Object}
     */
    var settings = {
      distance: 'm',
      speed: 'km/h',
      lift: 'm/s',
      altitude: 'm'
    };

    /**
     * A static dictionary of the supported units with its
     * conversion factors and formatting functions
     * @const
     * @type {Object}
     */
    var UNITS = {
      // Length
      'm': [1, slUnits.format_decimal],
      'ft': [3.28084, slUnits.format_decimal],
      'km': [1 / 1000., slUnits.format_decimal],
      'NM': [1 / 1852., slUnits.format_decimal],
      'mi': [1 / 1609.34, slUnits.format_decimal],

      // Speed
      'm/s': [1, function(value) {
        return slUnits.format_decimal(value, 1);
      }],
      'km/h': [3.6, function(value) {
        return slUnits.format_decimal(value, 1);
      }],
      'kt': [1.94384449, function(value) {
        return slUnits.format_decimal(value, 1);
      }],
      'mph': [2.23693629, function(value) {
        return slUnits.format_decimal(value, 1);
      }],
      'ft/min': [196.850394, slUnits.format_decimal]
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
      if (UNITS[distance]) settings.distance = distance;
      if (UNITS[speed]) settings.speed = speed;
      if (UNITS[lift]) settings.lift = lift;
      if (UNITS[altitude]) settings.altitude = altitude;
    };

    function generateFunctions(unit_type) {
      // Generate e.g. format_distance(value) functions
      slUnits['format_' + unit_type] = function(value) {
        value = slUnits['convert_' + unit_type](value);
        return slUnits['add_' + unit_type + '_unit'](value);
      };

      // Generate e.g. convert_distance(value) functions
      slUnits['convert_' + unit_type] = function(value) {
        return value * UNITS[settings[unit_type]][0];
      };

      // Generate e.g. add_distance_unit(value) functions
      slUnits['add_' + unit_type + '_unit'] = function(value) {
        value = UNITS[settings[unit_type]][1](value);
        return value + ' ' + settings[unit_type];
      };
    }

    for (var i = 0; i < UNIT_TYPES_LENGTH; ++i) {
      generateFunctions(UNIT_TYPES[i]);
    }
  };
})();
