


/**
 * An ordered collection of flight objects.
 * @constructor
 */
slFlightCollection = function() {
  var collection = slCollection();

  // Public attributes and methods

  var source = new ol.source.Vector();

  /**
   * Calculates the bounds of all flights in the collection.
   * @return {ol.extent}
   */
  collection.getBounds = function() {
    return source.getExtent();
  };

  /**
   * Returns the vector layer source of this collection.
   * @return {ol.source.Vector}
   */
  collection.getSource = function() {
    return source;
  };

  /**
   * Returns the minimum and maximum fix time within the extent.
   * Code based on ol.render.canvas.Replay.prototype.appendFlatCoordinates.
   * @param {ol.extent} extent
   * @return {Object}
   */
  collection.getMinMaxTimeInExtent = function(extent) {
    var min = Infinity,
        total_min = Infinity;
    var max = -Infinity,
        total_max = -Infinity;

    source.forEachFeatureInExtent(extent, function(f) {
      var coordinates = f.getGeometry().getCoordinates();

      var lastCoord = coordinates[0];
      var nextCoord = null;
      var end = coordinates.length;

      var lastRel = ol.extent.containsCoordinate(extent, lastCoord),
          nextRel;

      total_min = Math.min(total_min, lastCoord[3]);

      if (lastRel == true)
        min = Math.min(lastCoord[3], min);

      for (var i = 1; i < end; i += 1) {
        nextCoord = coordinates[i];

        nextRel = ol.extent.containsCoordinate(extent, nextCoord);

        // current vector completely within extent. do nothing.
        // current vector completely outside extent. do nothing.

        // last vertice was inside extent, next one is outside.
        if (lastRel && !nextRel) {
          max = Math.max(nextCoord[3], max);
          lastRel = nextRel;
        } else if (!lastRel && nextRel) {
          // last vertice was outside extent, next one is inside
          min = Math.min(lastCoord[3], min);
        }

        lastCoord = nextCoord;
        lastRel = nextRel;
      }

      if (lastRel == true)
        max = Math.max(lastCoord[3], max);

      total_max = Math.max(total_max, lastCoord[3]);
    });

    if (min == Infinity) min = total_min;
    if (max == -Infinity) max = total_max;

    return { min: min, max: max };
  };

  return collection;
};


/**
 * Array of flight objects. (see addFlight method)
 */
var flights = slFlightCollection();

var baro;
var fix_table;
var phase_tables = new Array();
var styles;

var phase_markers = {
  start: null,
  end: null
};

/*
 * Global time, can be:
 * null -> no time is set, don't show barogram crosshair/plane position
 * -1 -> always show the latest time/fix for each flight
 * >= 0 -> show the associated time in the barogram and on the map
 */
var default_time = null;
var global_time = default_time;
var playing = false;


/**
 * List of colors for flight path display
 */
var colors = ['#004bbd', '#bf0099', '#cf7c00', '#ff0000', '#00c994', '#ffff00'];
var contest_colors = {
  'olc_plus classic': '#ff2c73',
  'olc_plus triangle': '#9f14ff'
};


/**
 * Style function
 * @param {ol.feature} feature - Feature to style
 * @return {Array} style
 */
function style_function(feature) {
  if (!$.inArray('type', feature.getKeys()))
    return null;

  var color = '#004bbd'; // default color
  if ($.inArray('color', feature.getKeys()))
    color = feature.get('color');

  var z_index = 1000; // default z-index
  var line_dash = undefined; // default line style

  switch (feature.get('type')) {
    case 'flight':
      z_index = 1000;
      break;

    case 'contest':
      z_index = 999;
      line_dash = [5];
      break;
  }

  return [new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: color,
      width: 2,
      lineDash: line_dash
    }),
    zIndex: z_index
  })];
}


/**
 * Initialize the map and add airspace and flight path layers.
 */
function initFlightLayer() {
  var flight_path_layer = new ol.layer.Image({
    source: new ol.source.ImageVector({
      source: flights.getSource(),
      style: style_function
    }),
    name: 'Flight',
    z_index: 50
  });

  map.addLayer(flight_path_layer);

  var flight_contest_source = new ol.source.Vector({
    features: []
  });

  var flight_contest_layer = new ol.layer.Vector({
    source: flight_contest_source,
    style: style_function,
    name: 'Contest',
    z_index: 49
  });

  map.addLayer(flight_contest_layer);
  map.on('moveend', function(e) {
    if (updateBaroScale())
      baro.draw();
  });

  map.hover_enabled = true;

  map.play_button = new PlayButton();
  $(map.play_button).on('click touchend', function() {
    if (playing)
      stop();
    else
      play();
  });
  map.addControl(map.play_button);
}

function initFixTable() {
  fix_table = slFixTable($('#fix-data'));
  $(fix_table).on('selection_changed', function(e) {
    updateBaroData();
    baro.draw();
  });
  $(fix_table).on('remove_flight', function(e, sfid) {
    removeFlight(sfid);
  });
}

initFixTable();

function updateBaroScale() {
  var extent = map.getView().calculateExtent(map.getSize());
  var interval = flights.getMinMaxTimeInExtent(extent);

  var redraw = false;

  if (interval.max == -Infinity) {
    baro.clearTimeInterval();
    redraw = true;
  } else {
    redraw = baro.setTimeInterval(interval.min, interval.max);
  }

  return redraw;
}


/**
 * Add a flight to the map and barogram.
 *
 * Note: _lonlat, _levels, _time, _enl, and _height MUST have the same number
 *   of elements when decoded.
 *
 * @param {int} sfid SkyLines flight ID.
 * @param {String} _lonlat Google polyencoded string of geolocations
 *   (lon + lat, WSG 84).
 * @param {String} _time Google polyencoded string of time values.
 * @param {String} _height Google polyencoded string of height values.
 * @param {String} _enl Google polyencoded string of engine noise levels.
 * @param {Array(Objects)} _contests Array of scored/optimised contests.
 *   Such an object must contain: name, turnpoints, times
 *   turnpoints and times are googlePolyEncoded strings.
 * @param {String} _elevations_t Google polyencoded string of elevation
 *   time values.
 * @param {String} _elevations_h Google polyencoded string of elevations.
 * @param {Object=} opt_additional May contain additional information about
 *   the flight, e.g. registration number, callsign, ...
 */
function addFlight(sfid, _lonlat, _time, _height, _enl,
    _contests, _elevations_t, _elevations_h, opt_additional) {
  var _additional = opt_additional || {};

  var height = ol.format.Polyline.decodeDeltas(_height, 1, 1);
  var time = ol.format.Polyline.decodeDeltas(_time, 1, 1);
  var enl = ol.format.Polyline.decodeDeltas(_enl, 1, 1);
  var lonlat = ol.format.Polyline.decodeDeltas(_lonlat, 2);

  var coordinates = new ol.geom.LineString([], 'XYZM');

  var lonlatLength = lonlat.length;
  for (var i = 0; i < lonlatLength; i += 2) {
    var point = ol.proj.transform([lonlat[i + 1], lonlat[i]],
                                  'EPSG:4326', 'EPSG:3857');
    coordinates.appendCoordinate([point[0], point[1],
                                  height[i / 2], time[i / 2]]);
  }

  var color = _additional.color || colors[flights.length() % colors.length];

  var feature = new ol.Feature({
    geometry: coordinates,
    sfid: sfid,
    color: color,
    type: 'flight'
  });

  flights.getSource().addFeature(feature);

  var contests = [];
  if (_contests) {
    var _contestsLength = _contests.length;
    for (var i = 0; i < _contestsLength; ++i) {
      var contest = _contests[i];
      var turnpoints = ol.format.Polyline.decodeDeltas(contest.turnpoints, 2);
      var times = ol.format.Polyline.decodeDeltas(contest.times, 1, 1);

      var name = contest.name;
      contests.push({
        name: name,
        color: contest_colors[name],
        turnpoints: turnpoints,
        times: times
      });

      addContest(name, turnpoints, times, sfid);
    }
  }

  var flot_h = [], flot_enl = [];
  var timeLength = time.length;
  for (var i = 0; i < timeLength; ++i) {
    var timestamp = time[i] * 1000;
    flot_h.push([timestamp, slUnits.convertAltitude(height[i])]);
    flot_enl.push([timestamp, enl[i]]);
  }

  // Add flight as a row to the fix data table
  fix_table.addRow(sfid, color, _additional['competition_id']);

  var _elev_t = ol.format.Polyline.decodeDeltas(_elevations_t, 1, 1);
  var _elev_h = ol.format.Polyline.decodeDeltas(_elevations_h, 1, 1);

  var flot_elev = [], elev_t = [], elev_h = [];
  for (var i = 0; i < _elev_t.length; i++) {
    var timestamp = _elev_t[i] * 1000;
    var e = _elev_h[i];
    if (e < -500)
      e = null;

    elev_t.push(_elev_t[i]);
    elev_h.push(e);
    flot_elev.push([timestamp, e ? slUnits.convertAltitude(e) : null]);
  }

  flights.add({
    t: time,
    enl: enl,
    geo: coordinates,
    color: color,
    sfid: sfid,
    plane: { point: null, marker: null },
    last_update: time[time.length - 1],
    contests: contests,
    elev_t: elev_t,
    elev_h: elev_h,
    flot_h: flot_h,
    flot_enl: flot_enl,
    flot_elev: flot_elev,
    additional: _additional
  });

  updateBaroData();
  updateBaroScale();
  baro.draw();

  $('#wingman-table').find('*[data-sfid=' + sfid + ']')
      .find('.color-stripe').css('background-color', color);

  // Set fix data table into "selectable" mode if
  // more than one flight is loaded
  if (flights.length() > 1)
    fix_table.setSelectable(true);

  setTime(global_time);
}


/**
 * @param {string} url URL to fetch.
 * @param {boolean} async do asynchronous request (defaults true)
 */
function addFlightFromJSON(url, async) {
  $.ajax(url, {
    async: (typeof async === undefined) || async === true,
    success: function(data) {
      if (flights.has(data.sfid))
        return;

      addFlight(data.sfid, data.points,
                data.barogram_t, data.barogram_h,
                data.enl, data.contests,
                data.elevations_t, data.elevations_h, data.additional);

      map.render();
    }
  });
}


/**
 * Add a flight contest trace to the map
 *
 * @param {String} name Name to display.
 * @param {Array(Object)} lonlat Array of LonLat pairs.
 * @param {Array(Integer)} times Array of times.
 * @param {Integer} sfid The SkyLines flight id this contest trace belongs to.
 */
function addContest(name, lonlat, times, sfid) {
  var coordinates = new ol.geom.LineString([]);
  var lonlatLength = lonlat.length;

  var triangle = (name.search(/triangle/) != -1 && lonlatLength == 5 * 2);

  if (triangle) lonlatLength -= 2;

  for (var i = 0; i < lonlatLength; i += 2) {
    var point = ol.proj.transform([lonlat[i + 1], lonlat[i]],
                                  'EPSG:4326', 'EPSG:3857');
    coordinates.appendCoordinate(point);
  }

  if (triangle) {
    coordinates.appendCoordinate(coordinates.getFirstCoordinate());
  }

  var color = contest_colors[name] || '#ff2c73';
  var feature = new ol.Feature({
    geometry: coordinates,
    sfid: sfid,
    color: color,
    type: 'contest'
  });

  var contest_layer = map.getLayers().getArray().filter(function(e) {
    return e.get('name') == 'Contest';
  })[0];
  contest_layer.getSource().addFeature(feature);
}

function removeFlight(sfid) {
  // never remove the first flight...
  if (flights.at(0).sfid == sfid)
    return;

  var flight = flights.get(sfid);

  // this flight doesn't exist, do nothing...
  if (flight === null)
    return;

  // Hide plane to remove any additional related objects from the map
  hidePlaneOnMap(flight);

  var flight_layer = map.getLayers().getArray().filter(function(e) {
    return e.get('name') == 'Flight';
  })[0];
  flights.getSource().removeFeature(
      flights.getSource().getFeatures().filter(function(e) {
        return e.get('sfid') == sfid;
      })[0]
  );

  var contest_layer = map.getLayers().getArray().filter(function(e) {
    return e.get('name') == 'Contest';
  })[0];

  var contest_features = contest_layer.getSource().getFeatures()
    .filter(function(e) {
        return e.get('sfid') == sfid;
      });

  for (var i = 0; i < contest_features.length; i++)
    contest_layer.getSource().removeFeature(contest_features[i]);


  $('#wingman-table').find('*[data-sfid=' + sfid + ']')
      .find('.color-stripe').css('background-color', '');

  flights.remove(sfid);
  fix_table.removeRow(sfid);
  updateBaroData();
  updateBaroScale();
  baro.draw();
}


function play() {
  // if there are no flights, then there is nothing to animate
  if (flights.length == 0)
    return false;

  // if no time is set
  if (global_time == null || global_time == -1) {
    // find the first timestamp of all flights
    var start_time = Number.MAX_VALUE;
    flights.each(function(flight) {
      if (flight.t[0] < start_time)
        start_time = flight.t[0];
    });

    // start the animation at the beginning
    setTime(start_time);
  }

  // disable mouse hovering
  map.hover_enabled = false;
  baro.hover_enabled = false;

  // set play button to "stop" mode
  map.play_button.setMode('stop');

  // start animation
  playing = true;
  tick();
}


function stop() {
  // stop the tick() function if it is still running
  playing = false;

  // set play button to "play" mode
  map.play_button.setMode('play');

  // reenable mouse hovering
  map.hover_enabled = true;
  baro.hover_enabled = true;
}


function tick() {
  if (!playing)
    return;

  // increase time
  var time = global_time + 1;

  // find the last timestamp of all flights
  var stop_time = Number.MIN_VALUE;
  flights.each(function(flight) {
    var idx = flight.t.length - 1;
    if (flight.t[idx] > stop_time)
      stop_time = flight.t[idx];
  });

  // check if we are at the end of the animation
  if (time > stop_time) {
    stop();
    return;
  }

  // set the time for the new animation frame
  setTime(time);

  // schedule next call
  setTimeout(tick, 50);
}


/**
 * Searches the next smaller index to a number in a monotonic array.
 * If value == array[idx] it returns the next smaller index idx - 1
 * (the only way to return array.length - 1 is to search for values larger
 * than the last element). For values smaller than the first element
 * it returns 0.
 *
 * @param {Array} array Array.
 * @param {double} value Number.
 * @return {int} Index next smaller to Number in Array.
 */
function getNextSmallerIndex(array, value) {
  var low = 1;
  var high = array.length - 1;

  while (low < high) {
    var mid = (low + high) >> 1;
    if (value < array[mid]) high = mid;
    else low = mid + 1;
  }
  return low - 1;
}


/**
 * @param {int} seconds Seconds of day.
 * @return {String} formatted time "HH:MM:SS".
 */
function formatSecondsAsTime(seconds) {
  seconds %= 86400;
  var h = Math.floor(seconds / 3600);
  var m = Math.floor((seconds % 3600) / 60);
  var s = Math.floor(seconds % 3600 % 60);

  // Format the result into time strings
  return pad(h, 2) + ':' + pad(m, 2) + ':' + pad(s, 2);
}

function initBaro(element) {
  baro = slBarogram(element);

  var mouse_container_running = false;
  $(baro).on('barohover', function(event, time) {
    if (!baro.hover_enabled)
      return;

    if (mouse_container_running)
      return;

    mouse_container_running = true;

    setTimeout(function() {
      mouse_container_running = false;
    }, 25);

    setTime(time);
  }).on('baroclick', function(event, time) {
    setTime(time);
  }).on('mouseout', function(event) {
    if (!baro.hover_enabled)
      return;

    setTime(default_time);
  });

  baro.hover_enabled = true;
}

function updateBaroData() {
  var contests = [], elevations = [];

  var active = [], passive = [], enls = [];
  flights.each(function(flight) {
    var data = {
      data: flight.flot_h,
      color: flight.color
    };

    var enl_data = {
      data: flight.flot_enl,
      color: flight.color
    };

    if (fix_table.getSelection() && flight.sfid != fix_table.getSelection()) {
      passive.push(data);
    } else {
      active.push(data);
      enls.push(enl_data);
    }

    // Save contests of highlighted flight for later
    if (fix_table.getSelection() && flight.sfid == fix_table.getSelection()) {
      contests = flight.contests;
      elevations = flight.flot_elev;
    }

    // Save contests of only flight for later if applicable
    if (flights.length() == 1) {
      contests = flight.contests;
      elevations = flight.flot_elev;
    }
  });

  baro.setActiveTraces(active);
  baro.setPassiveTraces(passive);
  baro.setENLData(enls);
  baro.setContests(contests);
  baro.setElevations(elevations);
}

function setTime(time) {
  global_time = time;

  // if the mouse is not hovering over the barogram or any trail on the map
  if (!time) {
    // remove crosshair from barogram
    baro.clearTime();

    // remove plane icons from map
    hideAllPlanesOnMap();

    // remove data from fix-data table
    fix_table.clearAllFixes();

  } else {
    // update barogram crosshair
    baro.setTime(time);

    flights.each(function(flight) {
      // calculate fix data
      var fix_data = getFixData(flight, time);
      if (!fix_data) {
        // update map
        hidePlaneOnMap(flight);

        // update fix-data table
        fix_table.clearFix(flight.sfid);
      } else {
        // update map
        setPlaneOnMap(flight, fix_data);

        // update fix-data table
        fix_table.updateFix(flight.sfid, fix_data);
      }
    });
  }

  map.render();
  fix_table.render();
}

function getFixData(flight, time) {
  if (time == -1)
    time = flight.t[flight.t.length - 1];
  else if (time < flight.t[0] || time > flight.t[flight.t.length - 1])
    return null;

  var index = getNextSmallerIndex(flight.t, time);
  if (index < 0 || index >= flight.t.length - 1 ||
      flight.t[index] == undefined || flight.t[index + 1] == undefined)
    return null;

  var t_prev = flight.t[index];
  var t_next = flight.t[index + 1];
  var dt_total = t_next - t_prev;

  var fix_data = {};

  fix_data['time'] = t_prev;

  var _loc_prev = flight.geo.getCoordinateAtM(t_prev);
  var _loc_current = flight.geo.getCoordinateAtM(time);
  var _loc_next = flight.geo.getCoordinateAtM(t_next);

  fix_data['lon'] = _loc_current[0];
  fix_data['lat'] = _loc_current[1];

  fix_data['heading'] = Math.atan2(_loc_next[0] - _loc_prev[0],
                                   _loc_next[1] - _loc_prev[1]);

  fix_data['alt-msl'] = _loc_current[2];

  var loc_prev = ol.proj.transform(_loc_prev, 'EPSG:3857', 'EPSG:4326');
  var loc_next = ol.proj.transform(_loc_next, 'EPSG:3857', 'EPSG:4326');

  if (dt_total != 0) {
    fix_data['speed'] = geographicDistance(loc_next, loc_prev) / dt_total;
    fix_data['vario'] = (_loc_next[2] - _loc_prev[2]) / dt_total;
  }

  if (flight.elev_t !== undefined && flight.elev_h !== undefined) {
    var elev_index = getNextSmallerIndex(flight.elev_t, time);
    if (elev_index >= 0 && elev_index < flight.elev_t.length) {
      var elev = flight.elev_h[elev_index];
      if (elev) {
        fix_data['alt-gnd'] = fix_data['alt-msl'] - flight.elev_h[elev_index];
        if (fix_data['alt-gnd'] < 0)
          fix_data['alt-gnd'] = 0;
      }
    }
  }

  return fix_data;
}

function setPlaneOnMap(flight, fix_data) {
  var plane = flight.plane;

  // set plane location
  if (plane.point === null) {
    plane.point = new ol.geom.Point([fix_data['lon'], fix_data['lat']]);
  } else {
    plane.point.setCoordinates([fix_data['lon'], fix_data['lat']]);
  }

  // set plane heading
  // <heading> in radians
  plane['heading'] = fix_data['heading'];

  // add plane marker if more than one flight on the map
  if (flights.length() > 1) {
    if (plane.marker === null) {
      var badge = $('<span class="badge plane_marker" ' +
              'style="display: inline-block; text-align: center; ' +
              'background: ' + flight.color + ';">' +
          (flight.additional['competition_id'] || '') +
          '</span>');

      plane.marker = new ol.Overlay({
        element: badge
      });
      map.addOverlay(plane.marker);
      plane.marker.setOffset([badge.width(), -40]);
    }

    plane.marker.setPosition(plane.point.getCoordinates());
  }
}

function hidePlaneOnMap(flight) {
  var plane = flight.plane;

  plane.point = null;
  if (plane.marker !== null) {
    map.removeOverlay(plane.marker);
    plane.marker = null;
  }
}

function hideAllPlanesOnMap() {
  flights.each(hidePlaneOnMap);
}


/**
 * Handles the mouseover events over the map to display near airplanes
 */
function hoverMap() {
  // search on every mousemove over the map viewport. Run this function only
  // every 25ms to save some computing power.
  //var running = false;

  var msie_8 = $.browser.msie && (parseInt($.browser.version, 10) < 9);

  var style = new ol.style.Icon({
    anchor: [0.5, 0.5],
    anchorXUnits: 'fraction',
    anchorYUnits: 'fraction',
    size: [40, 24],
    src: msie_8 ?
        '/images/glider_symbol_msie.png' : '/images/glider_symbol.png',
    rotation: 0,
    rotateWithView: true
  });

  style.load();

  map.on('pointermove', function(e) {
    if (!map.hover_enabled || e.dragging)
      return;

    var coordinate = map.getEventCoordinate(e.originalEvent);
    displaySnap(coordinate);
  });

  map.on('postcompose', function(e) {
    var vector_context = e.vectorContext;

    flights.each(function(flight) {
      if (flight.plane.point !== null) {
        style.setRotation(flight.plane['heading']);
        vector_context.setImageStyle(style);
        vector_context.drawPointGeometry(flight.plane.point);
      }
    });
  });

  function displaySnap(coordinate) {
    var flight_path_source = flights.getSource();

    var closest_feature = flight_path_source
        .getClosestFeatureToCoordinate(coordinate);

    if (closest_feature !== null) {
      var geometry = closest_feature.getGeometry();
      var closest_point = geometry.getClosestPoint(coordinate);

      var feature_pixel = map.getPixelFromCoordinate(closest_point);
      var mouse_pixel = map.getPixelFromCoordinate(coordinate);

      var squared_distance = Math.pow(mouse_pixel[0] - feature_pixel[0], 2) +
                             Math.pow(mouse_pixel[1] - feature_pixel[1], 2);

      if (squared_distance > 100) {
        setTime(default_time);
      } else {
        var time = closest_point[3];
        setTime(time);
      }
    }

    map.render();
  }
}


/**
 * @param {DOMElement} placeholder DOM element of the phases table.
*/
function initPhasesTable(placeholder) {
  if (placeholder.length === 0 || placeholder.data('phase_table')) return;

  var phase_table = slPhaseTable(placeholder);

  placeholder.data('phase_table', phase_table);
  phase_tables.push(phase_table);

  $(phase_table)
      .on('selection_changed', function(event, data) {
        if (data) {
          phase_markers = highlightFlightPhase(data.start, data.end);
          baro.setTimeHighlight(data.start, data.end);

          for (var i = 0; i < phase_tables.length; i++) {
            if (phase_tables[i] != this) {
              phase_tables[i].setSelection(null, false);
            }
          }
        } else {
          phase_markers.start = null;
          phase_markers.end = null;

          baro.clearTimeHighlight();
        }

        baro.draw();
        map.render();
      });

  var phase_start_marker_style = new ol.style.Icon({
    anchor: [0.5, 1],
    anchorXUnits: 'fraction',
    anchorYUnits: 'fraction',
    src: '/vendor/openlayers/img/marker-green.png'
  });

  var phase_end_marker_style = new ol.style.Icon({
    anchor: [0.5, 1],
    anchorXUnits: 'fraction',
    anchorYUnits: 'fraction',
    src: '/vendor/openlayers/img/marker.png'
  });

  phase_start_marker_style.load();
  phase_end_marker_style.load();

  map.on('postcompose', function(e) {
    var vector_context = e.vectorContext;

    if (phase_markers.start !== null) {
      vector_context.setImageStyle(phase_start_marker_style);
      vector_context.drawPointGeometry(phase_markers.start);
      vector_context.setImageStyle(phase_end_marker_style);
      vector_context.drawPointGeometry(phase_markers.end);
    }
  });
}

function highlightFlightPhase(start, end) {
  // the phases table should contain only phases of our first flight only
  var flight = flights.at(0);

  var start_index = getNextSmallerIndex(flight.t, start);
  var end_index = getNextSmallerIndex(flight.t, end);

  var phase_markers = {
    start: null,
    end: null
  };

  if (start_index >= end_index) return phase_markers;

  var extent = ol.extent.boundingExtent(
      flight.geo.getCoordinates().slice(start_index, end_index + 1)
      );

  var view = map.getView();
  var buffer = Math.max(ol.extent.getWidth(extent),
                        ol.extent.getHeight(extent));
  view.fitExtent(ol.extent.buffer(extent, buffer * 0.05), map.getSize());

  var start_point = flight.geo.getCoordinates()[start_index];
  var end_point = flight.geo.getCoordinates()[end_index];

  phase_markers.start = new ol.geom.Point([start_point[0], start_point[1]]);
  phase_markers.end = new ol.geom.Point([end_point[0], end_point[1]]);

  return phase_markers;
}


/**
 * Moves the map to the last fix of a flight
 *
 * @param {int} sfid SkyLines flight ID.
 */
function followFlight(sfid) {
  if (!sfid) return;

  var flight = flights.get(sfid);
  if (flight) {
    var coordinate = flight.geo.getLastCoordinate();

    var pan = ol.animation.pan({
      duration: 200,
      source: (map.getView().getCenter())
    });

    map.beforeRender(pan);
    map.getView().setCenter(coordinate);
  }
}


function geographicDistance(loc1_deg, loc2_deg) {
  var radius = 6367009;

  var loc1 = [loc1_deg[0] * Math.PI / 180, loc1_deg[1] * Math.PI / 180];
  var loc2 = [loc2_deg[0] * Math.PI / 180, loc2_deg[1] * Math.PI / 180];

  var dlon = loc2[1] - loc1[1];
  var dlat = loc2[0] - loc1[0];

  var a = Math.pow(Math.sin(dlat / 2), 2) +
          Math.cos(loc1[0]) * Math.cos(loc2[0]) *
          Math.pow(Math.sin(dlon / 2), 2);
  var c = 2 * Math.asin(Math.sqrt(a));

  return radius * c;
}
