// Unit presets
distance_units = {
    'm': function(value) { return format_number(value) },
    'km': function(value) { return format_number(value / 1000.) },
    'NM': function(value) { return format_number(value / 1852.) },
    'mi': function(value) { return format_number(value / 1609.34) }
};

speed_units = {
    'm/s': function(value) { return format_decimal(value, 2) },
    'km/h': function(value) { return format_decimal(value * 3.6, 2) },
    'kt': function(value) { return format_decimal(value * 1.94384449, 2) },
    'mph': function(value) { return format_decimal(value * 2.23693629, 2) }
};

lift_units = {
    'm/s': function(value) { return format_decimal(value, 2) },
    'kt': function(value) { return format_decimal(value * 1.94384449, 2) },
    'ft/min': function(value) { return format_decimal(value * 196.850394, 2) }
};

altitude_units = {
    'm': function(value) { return format_number(value) },
    'ft': function(value) { return format_number(value * 3.2808399) }
};


// default units
DISTANCE_UNIT = 'm';
SPEED_UNIT = 'km/h';
LIFT_UNIT = 'm/s';
ALTITUDE_UNIT = 'm';

// generic number formatter function
function format_number(value) {
  return Math.round(value);
}

function format_decimal(value, decimals) {
  return value.toFixed(decimals);
}

// unit formatter functions
function format_distance(value) {
  return add_distance_unit(convert_distance(value));
}

function format_speed(value) {
  return add_speed_unit(convert_speed(value));
}

function format_lift(value) {
  return add_lift_unit(convert_lift(value));
}

function format_altitude(value) {
  return add_altitude_unit(convert_altitude(value));
}

// unit conversion functions
function convert_distance(value) {
  return distance_units[DISTANCE_UNIT](value);
}

function convert_speed(value) {
  return speed_units[SPEED_UNIT](value);
}

function convert_lift(value) {
  return lift_units[LIFT_UNIT](value);
}

function convert_altitude(value) {
  return altitude_units[ALTITUDE_UNIT](value);
}

// unit name functions
function add_distance_unit(value) {
  return value + ' ' + DISTANCE_UNIT;
}

function add_speed_unit(value) {
  return value + ' ' + SPEED_UNIT;
}

function add_lift_unit(value) {
  return value + ' ' + LIFT_UNIT;
}

function add_altitude_unit(value) {
  return value + ' ' + ALTITUDE_UNIT;
}

// initialisation
function initUnits(distance, speed, lift, altitude) {
  DISTANCE_UNIT = distance_units[distance] ? distance : 'km';
  SPEED_UNIT = speed_units[speed] ? speed : 'km/h';
  LIFT_UNIT = lift_units[lift] ? lift : 'm/s';
  ALTITUDE_UNIT = altitude_units[altitude] ? altitude : 'm';
}

