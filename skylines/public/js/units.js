(function() {
  slUnits = new function() {
    var slUnits = this;

    /**
     * @expose
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

    /**
     * The list of supported unit types.
     * For each type the corresponding functions are generated dynamically.
     * @const
     * @type {Array}
     */
    var UNIT_TYPES = ['distance', 'speed', 'lift', 'altitude'];

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
      distance: 'm',
      speed: 'km/h',
      lift: 'm/s',
      altitude: 'm'
    };

    /**
     * @expose
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
        value = slUnits.format_decimal(value, UNITS[settings[unit_type]][1]);
        return value + ' ' + settings[unit_type];
      };
    }

    for (var i = 0; i < UNIT_TYPES_LENGTH; ++i) {
      generateFunctions(UNIT_TYPES[i]);
    }
  };
})();
