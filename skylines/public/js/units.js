(function() {
  slUnits = new function() {
    var UNIT_TYPES = ['distance', 'speed', 'lift', 'altitude'];
    var UNIT_TYPES_LENGTH = UNIT_TYPES.length;

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

    for (var i = 0; i < UNIT_TYPES_LENGTH; ++i) {
      var unit_type = UNIT_TYPES[i];

      // Generate e.g. format_distance(value) functions
      this['format_' + unit_type] = function(value) {
        value = this['convert_' + unit_type](value);
        return this['add_' + unit_type + '_unit'](value);
      };

      // Generate e.g. convert_distance(value) functions
      this['convert_' + unit_type] = function(value) {
        var setting = settings[unit_type];
        return UNITS[setting](value);
      };

      // Generate e.g. add_distance_unit(value) functions
      this['add_' + unit_type + '_unit'] = function(value) {
        return value + ' ' + settings[unit_type];
      };
    }
  };
})();
