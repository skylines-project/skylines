(function() {
  slUnits = new function() {
    // default units
    var distance_unit = 'm';
    var speed_unit = 'km/h';
    var lift_unit = 'm/s';
    var altitude_unit = 'm';

    // Unit presets
    var UNITS = {
      'm': function(value) { return slUnits.format_decimal(value) },
      'ft': function(value) { return slUnits.format_decimal(value * 3.28084) },
      'km': function(value) { return slUnits.format_decimal(value / 1000.) },
      'NM': function(value) { return slUnits.format_decimal(value / 1852.) },
      'mi': function(value) { return slUnits.format_decimal(value / 1609.34) },

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

    // initialisation
    this.init = function(distance, speed, lift, altitude) {
      if (UNITS[distance]) distance_unit = distance;
      if (UNITS[speed]) speed_unit = speed;
      if (UNITS[lift]) lift_unit = lift;
      if (UNITS[altitude]) altitude_unit = altitude;
    };

    // generic number formatter function
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
      return UNITS[distance_unit](value);
    };

    this.convert_speed = function(value) {
      return UNITS[speed_unit](value);
    };

    this.convert_lift = function(value) {
      return UNITS[lift_unit](value);
    };

    this.convert_altitude = function(value) {
      return UNITS[altitude_unit](value);
    };

    // unit name functions
    this.add_distance_unit = function(value) {
      return value + ' ' + distance_unit;
    };

    this.add_speed_unit = function(value) {
      return value + ' ' + speed_unit;
    };

    this.add_lift_unit = function(value) {
      return value + ' ' + lift_unit;
    };

    this.add_altitude_unit = function(value) {
      return value + ' ' + altitude_unit;
    };
  };
})();
