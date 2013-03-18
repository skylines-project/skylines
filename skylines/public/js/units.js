(function() {
  slUnits = new function() {
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
      'm': function(value) {
        return slUnits.format_decimal(value);
      },
      'ft': function(value) {
        return slUnits.format_decimal(value * 3.28084);
      },
      'km': function(value) {
        return slUnits.format_decimal(value / 1000.);
      },
      'NM': function(value) {
        return slUnits.format_decimal(value / 1852.);
      },
      'mi': function(value) {
        return slUnits.format_decimal(value / 1609.34);
      },

      // Speed
      'm/s': function(value) {
        return slUnits.format_decimal(value, 1);
      },
      'km/h': function(value) {
        return slUnits.format_decimal(value * 3.6, 1);
      },
      'kt': function(value) {
        return slUnits.format_decimal(value * 1.94384449, 1);
      },
      'mph': function(value) {
        return slUnits.format_decimal(value * 2.23693629, 1);
      },
      'ft/min': function(value) {
        return slUnits.format_decimal(value * 196.850394);
      }
    };

    /**
     * Initialises the slUnits module with the user settings
     *
     * @param {String} distance The distance unit (e.g. 'km').
     * @param {String} speed The speed unit (e.g. 'km/h').
     * @param {String} lift The vertical speed unit (e.g. 'm/s').
     * @param {String} altitude The altitude unit (e.g. 'm').
     */
    this.init = function(distance, speed, lift, altitude) {
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
    this.format_decimal = function(value, decimals) {
      return value.toFixed(decimals);
    };

    // unit formatter functions
    this.format_distance = function(value) {
      return this.add_distance_unit(this.convert_distance(value));
    };

    this.format_speed = function(value) {
      return this.add_speed_unit(this.convert_speed(value));
    };

    this.format_lift = function(value) {
      return this.add_lift_unit(this.convert_lift(value));
    };

    this.format_altitude = function(value) {
      return this.add_altitude_unit(this.convert_altitude(value));
    };

    // unit conversion functions
    this.convert_distance = function(value) {
      return UNITS[settings.distance](value);
    };

    this.convert_speed = function(value) {
      return UNITS[settings.speed](value);
    };

    this.convert_lift = function(value) {
      return UNITS[settings.lift](value);
    };

    this.convert_altitude = function(value) {
      return UNITS[settings.altitude](value);
    };

    // unit name functions
    this.add_distance_unit = function(value) {
      return value + ' ' + settings.distance;
    };

    this.add_speed_unit = function(value) {
      return value + ' ' + settings.speed;
    };

    this.add_lift_unit = function(value) {
      return value + ' ' + settings.lift;
    };

    this.add_altitude_unit = function(value) {
      return value + ' ' + settings.altitude;
    };
  };
})();
