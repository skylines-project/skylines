(function() {
  slUnits = new function() {
    // initialisation
    this.init = function(distance, speed, lift, altitude) {
      DISTANCE_UNIT = distance_units[distance] ? distance : 'km';
      SPEED_UNIT = speed_units[speed] ? speed : 'km/h';
      LIFT_UNIT = lift_units[lift] ? lift : 'm/s';
      ALTITUDE_UNIT = altitude_units[altitude] ? altitude : 'm';
    };

    // Unit presets
    var distance_units = {
      'm': function(value) { return slUnits.format_number(value) },
      'km': function(value) { return slUnits.format_number(value / 1000.) },
      'NM': function(value) { return slUnits.format_number(value / 1852.) },
      'mi': function(value) { return slUnits.format_number(value / 1609.34) }
    };

    var speed_units = {
      'm/s': function(value) {
        return slUnits.format_decimal(value, 2);
      },
      'km/h': function(value) {
        return slUnits.format_decimal(value * 3.6, 2);
      },
      'kt': function(value) {
        return slUnits.format_decimal(value * 1.94384449, 2);
      },
      'mph': function(value) {
        return slUnits.format_decimal(value * 2.23693629, 2);
      }
    };

    var lift_units = {
      'm/s': function(value) {
        return slUnits.format_decimal(value, 2);
      },
      'kt': function(value) {
        return slUnits.format_decimal(value * 1.94384449, 2);
      },
      'ft/min': function(value) {
        return slUnits.format_decimal(value * 196.850394, 2);
      }
    };

    var altitude_units = {
      'm': function(value) { return slUnits.format_number(value) },
      'ft': function(value) { return slUnits.format_number(value * 3.2808399) }
    };

    // default units
    var DISTANCE_UNIT = 'm';
    var SPEED_UNIT = 'km/h';
    var LIFT_UNIT = 'm/s';
    var ALTITUDE_UNIT = 'm';

    // generic number formatter function
    this.format_number = function(value) {
      return Math.round(value);
    };

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
      return distance_units[DISTANCE_UNIT](value);
    };

    this.convert_speed = function(value) {
      return speed_units[SPEED_UNIT](value);
    };

    this.convert_lift = function(value) {
      return lift_units[LIFT_UNIT](value);
    };

    this.convert_altitude = function(value) {
      return altitude_units[ALTITUDE_UNIT](value);
    };

    // unit name functions
    this.add_distance_unit = function(value) {
      return value + ' ' + DISTANCE_UNIT;
    };

    this.add_speed_unit = function(value) {
      return value + ' ' + SPEED_UNIT;
    };

    this.add_lift_unit = function(value) {
      return value + ' ' + LIFT_UNIT;
    };

    this.add_altitude_unit = function(value) {
      return value + ' ' + ALTITUDE_UNIT;
    };
  };
})();
