(function() {
  slUnits = new function() {
    // default units
    var settings = {
      distance: 'm',
      speed: 'km/h',
      lift: 'm/s',
      altitude: 'm'
    };

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
      if (UNITS[distance]) settings.distance = distance;
      if (UNITS[speed]) settings.speed = speed;
      if (UNITS[lift]) settings.lift = lift;
      if (UNITS[altitude]) settings.altitude = altitude;
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
