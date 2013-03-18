(function() {
  slUnits = new function() {
    var slUnits = this;

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
      'm': [1, function(value) {
        return slUnits.format_decimal(value);
      }],
      'ft': [3.28084, function(value) {
        return slUnits.format_decimal(value);
      }],
      'km': [1 / 1000., function(value) {
        return slUnits.format_decimal(value);
      }],
      'NM': [1 / 1852., function(value) {
        return slUnits.format_decimal(value);
      }],
      'mi': [1 / 1609.34, function(value) {
        return slUnits.format_decimal(value);
      }],

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
      'ft/min': [196.850394, function(value) {
        return slUnits.format_decimal(value);
      }]
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

    // unit formatter functions
    slUnits.format_distance = function(value) {
      return slUnits.add_distance_unit(slUnits.convert_distance(value));
    };

    slUnits.format_speed = function(value) {
      return slUnits.add_speed_unit(slUnits.convert_speed(value));
    };

    slUnits.format_lift = function(value) {
      return slUnits.add_lift_unit(slUnits.convert_lift(value));
    };

    slUnits.format_altitude = function(value) {
      return slUnits.add_altitude_unit(slUnits.convert_altitude(value));
    };

    // unit conversion functions
    slUnits.convert_distance = function(value) {
      return value * UNITS[settings.distance][0];
    };

    slUnits.convert_speed = function(value) {
      return value * UNITS[settings.speed][0];
    };

    slUnits.convert_lift = function(value) {
      return value * UNITS[settings.lift][0];
    };

    slUnits.convert_altitude = function(value) {
      return value * UNITS[settings.altitude][0];
    };

    // unit name functions
    slUnits.add_distance_unit = function(value) {
      value = UNITS[settings.distance][1](value);
      return value + ' ' + settings.distance;
    };

    slUnits.add_speed_unit = function(value) {
      value = UNITS[settings.speed][1](value);
      return value + ' ' + settings.speed;
    };

    slUnits.add_lift_unit = function(value) {
      value = UNITS[settings.lift][1](value);
      return value + ' ' + settings.lift;
    };

    slUnits.add_altitude_unit = function(value) {
      value = UNITS[settings.altitude][1](value);
      return value + ' ' + settings.altitude;
    };
  };
})();
