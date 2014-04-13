/**
 * An ordered collection of flight objects.
 * @constructor
 */
slFlightCollection = function() {
  var collection = slCollection();

  // Public attributes and methods

  /**
   * Calculates the bounds of all flights in the collection.
   * @return {OpenLayers.Bounds}
   */
  collection.getBounds = function() {
    var bounds = new OpenLayers.Bounds();

    collection.each(function(flight) {
      bounds.extend(flight.geo.bounds);
    });

    return bounds;
  };

  return collection;
};


/**
 * Array of flight objects. (see addFlight method)
 */
var flights = slFlightCollection();

var baro;
var fix_table;
var phase_table;
var phases_layer;


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
 * Initialize the map and add airspace and flight path layers.
 */

function initFlightLayer() {
  var default_style = new OpenLayers.Style({
    strokeColor: '${color}',
    strokeWidth: 2,
    graphicZIndex: 1000
  });

  var contest_style = new OpenLayers.Style({
    strokeColor: '${color}',
    strokeWidth: 2,
    strokeDashstyle: 'dash',
    graphicZIndex: 1500
  });

  var plane_style = new OpenLayers.Style({
    // Set the external graphic and background graphic images.
    externalGraphic: '${getGraphic}',
    // Makes sure the background graphic is placed correctly relative
    // to the external graphic.
    graphicXOffset: -20,
    graphicYOffset: -8,
    graphicWidth: 40,
    graphicHeight: 24,
    rotation: '${rotation}',
    // Set the z-indexes of both graphics to make sure the background
    // graphics stay in the background (shadows on top of markers looks
    // odd; let's not do that).
    graphicZIndex: 2000
  }, {
    context: {
      getGraphic: function(feature) {
        var msie_8 = $.browser.msie && (parseInt($.browser.version, 10) < 9);
        var normal_glider = msie_8 ?
            '/images/glider_symbol_msie.png' : '/images/glider_symbol.png';
        return normal_glider;
      }
    }
  });

  var hidden_style = new OpenLayers.Style({
    display: 'none'
  });

  var flightPathLayer = new OpenLayers.Layer.Vector('Flight', {
    styleMap: new OpenLayers.StyleMap({
      'default': default_style,
      'contest': contest_style,
      'plane': plane_style,
      'hidden': hidden_style
    }),
    rendererOptions: {
      zIndexing: true
    },
    displayInLayerSwitcher: false
  });

  map.addLayer(flightPathLayer);

  map.events.register('move', null, function() {
    initRedrawLayer(flightPathLayer);
  });

  map.events.register('moveend', null, updateBaroScale);

  map.hover_enabled = true;

  map.play_button = new PlayButton();
  $(map.play_button).on('click', function() {
    if (playing)
      stop();
    else
      play();
  });
  map.addControl(map.play_button);
}

function initFixTable() {
  fix_table = slFixTable($('#fix-data'));
  $(fix_table).on('selection_changed', updateBaroData);
}

initFixTable();

function updateBaroScale() {
  var first_t = 999999;
  var last_t = 0;

  // circle throu all flights
  flights.each(function(flight) {
    var geometries = flight.geo.partitionedGeometries;

    // if flight is not in viewport continue.
    var length = geometries.length;
    if (length == 0)
      return;

    // show barogram of all trace parts visible
    var comp_length = geometries[length - 1].components.length;
    var first = geometries[0].components[0].originalIndex;
    var last = geometries[length - 1].components[comp_length - 1].originalIndex;

    // get first and last time which should be the bounds of the barogram
    if (flight.t[first] < first_t)
      first_t = flight.t[first];

    if (flight.t[last] > last_t)
      last_t = flight.t[last];
  });

  var redraw = false;

  if (last_t == 0) {
    baro.clearTimeInterval();
    redraw = true;
  } else {
    redraw = baro.setTimeInterval(first_t, last_t);
  }

  if (redraw) baro.draw();
}


/**
 * Initiates the redraw of a layer
 *
 * @this {Object}
 * @param {OpenLayers.Layer} layer The layer that should be redrawn.
 */
function initRedrawLayer(layer) {
  // Run this function only every 50ms to save some computing power.
  if (this.initRedrawLayerRunning) return;

  this.initRedrawLayerRunning = true;
  setTimeout(function() { this.initRedrawLayerRunning = false; }, 50);

  layer.redraw();
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
 * @param {String} _levels Google polyencoded string of levels of detail.
 * @param {int} _num_levels Number of levels encoded in _lonlat and _levels.
 * @param {String} _time Google polyencoded string of time values.
 * @param {String} _height Google polyencoded string of height values.
 * @param {String} _enl Google polyencoded string of engine noise levels.
 * @param {Array(double)} zoom_levels Array of zoom levels where to switch
 *   between the LoD.
 * @param {Array(Objects)} _contests Array of scored/optimised contests.
 *   Such an object must contain: name, turnpoints, times
 *   turnpoints and times are googlePolyEncoded strings.
 * @param {String} _elevations_t Google polyencoded string of elevation
 *   time values.
 * @param {String} _elevations_h Google polyencoded string of elevations.
 * @param {Object=} opt_additional May contain additional information about
 *   the flight, e.g. registration number, callsign, ...
 */
function addFlight(sfid, _lonlat, _levels, _num_levels, _time, _height, _enl,
    zoom_levels, _contests, _elevations_t, _elevations_h, opt_additional) {
  var _additional = opt_additional || {};

  var polyline_decoder = new OpenLayers.Format.EncodedPolyline();

  var height = polyline_decoder.decodeDeltas(_height, 1, 1);
  var time = polyline_decoder.decodeDeltas(_time, 1, 1);
  var enl = polyline_decoder.decodeDeltas(_enl, 1, 1);
  var lonlat = polyline_decoder.decode(_lonlat, 2);
  var lod = polyline_decoder.decodeUnsignedIntegers(_levels);

  var points = new Array();
  var lonlatLength = lonlat.length;
  for (var i = 0; i < lonlatLength; ++i) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i][1], lonlat[i][0]).
        transform(WGS84_PROJ, map.getProjectionObject()));
  }

  // add new flight
  var flight = new OpenLayers.Geometry.ProgressiveLineString(
      points, lod, zoom_levels);
  flight.clip = 1;

  var color = _additional.color || colors[flights.length() % colors.length];
  var feature = new OpenLayers.Feature.Vector(flight, { color: color });

  var plane = new OpenLayers.Feature.Vector(points[0], { rotation: 0 });
  plane.renderIntent = 'plane';

  map.getLayersByName('Flight')[0].addFeatures([feature, plane]);

  var contests = [];
  if (_contests) {
    var _contestsLength = _contests.length;
    for (var i = 0; i < _contestsLength; ++i) {
      var contest = _contests[i];
      var turnpoints = polyline_decoder.decode(contest.turnpoints, 2);
      var times = polyline_decoder.decodeDeltas(contest.times, 1, 1);

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

  var _elev_t = polyline_decoder.decodeDeltas(_elevations_t, 1, 1);
  var _elev_h = polyline_decoder.decodeDeltas(_elevations_h, 1, 1);

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
    lonlat: lonlat,
    t: time,
    h: height,
    enl: enl,
    geo: flight,
    color: color,
    plane: plane,
    sfid: sfid,
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

  // Set fix data table into "selectable" mode if
  // more than one flight is loaded
  if (flights.length() > 1)
    fix_table.setSelectable(true);

  setTime(global_time);
}


/**
 * @param {string} url URL to fetch.
 */
function addFlightFromJSON(url) {
  $.ajax(url, {
    success: function(data) {
      if (flights.has(data.sfid))
        return;

      addFlight(data.sfid, data.encoded.points, data.encoded.levels,
                data.num_levels, data.barogram_t, data.barogram_h,
                data.enl, data.zoom_levels, data.contests,
                data.elevations_t, data.elevations_h, data.additional);

      initRedrawLayer(map.getLayersByName('Flight')[0]);
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
  var points = new Array();
  var lonlatLength = lonlat.length;

  var triangle = (name.search(/triangle/) != -1 && lonlatLength == 5);

  if (triangle) lonlatLength--;

  for (var i = 0; i < lonlatLength; ++i) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i][1], lonlat[i][0]).
        transform(WGS84_PROJ, map.getProjectionObject()));
  }

  if (triangle) {
    points[0] = points[3];
  }

  var trace = new OpenLayers.Geometry.LineString(points);

  var color = contest_colors[name] || '#ff2c73';
  var feature = new OpenLayers.Feature.Vector(trace, {
    color: color,
    sfid: sfid
  });

  // show the contest traces only for the first flight by default
  feature.renderIntent = (flights.length() == 0) ? 'contest' : 'hidden';

  map.getLayersByName('Flight')[0].addFeatures(feature);
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
 * Searches the next smaller index to a number in a monotonic array
 *
 * @param {Array} array Array.
 * @param {double} value Number.
 * @return {int} Index next smaller to Number in Array.
 */
function getNextSmallerIndex(array, value) {
  var length = array.length;

  if (length < 2)
    return length - 1;

  for (length; --length;) {
    if (array[length] < value)
      break;
  }

  return length;
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

  baro.draw();
}

function setTime(time) {
  global_time = time;

  // remove plane icons from map
  hideAllPlanesOnMap();

  // if the mouse is not hovering over the barogram or any trail on the map
  if (!time) {
    // remove crosshair from barogram
    baro.clearTime();

    // remove data from fix-data table
    fix_table.clearAllFixes();
    fix_table.render();

    return;
  }

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
  var dt_rel = 0;

  if (dt_total != 0)
    dt_rel = (time - t_prev) / dt_total;

  var fix_data = {};

  fix_data['time'] = t_prev;

  var loc_prev = flight.lonlat[index];
  var loc_next = flight.lonlat[index + 1];

  var lon_prev = loc_prev[1], lat_prev = loc_prev[0];
  var lon_next = loc_next[1], lat_next = loc_next[0];

  var _loc_prev = new OpenLayers.Geometry.Point(lon_prev, lat_prev);
  _loc_prev.transform(WGS84_PROJ, map.getProjectionObject());
  var _loc_next = new OpenLayers.Geometry.Point(lon_next, lat_next);
  _loc_next.transform(WGS84_PROJ, map.getProjectionObject());

  fix_data['lon'] = lon_prev + (lon_next - lon_prev) * dt_rel;
  fix_data['lat'] = lat_prev + (lat_next - lat_prev) * dt_rel;

  fix_data['loc'] = new OpenLayers.Geometry.Point(
      fix_data['lon'], fix_data['lat']);
  fix_data['loc'].transform(WGS84_PROJ, map.getProjectionObject());

  fix_data['heading'] = Math.atan2(_loc_next.x - _loc_prev.x,
                                   _loc_next.y - _loc_prev.y) * 180 / Math.PI;

  if (dt_total != 0)
    fix_data['speed'] = OpenLayers.Util.distVincenty(
        {lon: loc_next[1], lat: loc_next[0]},
        {lon: loc_prev[1], lat: loc_prev[0]}) * 1000 / dt_total;

  var h_prev = flight.h[index];
  var h_next = flight.h[index + 1];

  fix_data['alt-msl'] = h_prev;

  if (dt_total != 0)
    fix_data['vario'] = (h_next - h_prev) / dt_total;

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
  plane.geometry = fix_data['loc'];

  // set plane heading
  // <heading> in degrees
  plane.attributes.rotation = fix_data['heading'];

  // add plane to map
  map.getLayersByName('Flight')[0].addFeatures(plane);

  // add plane marker if more than one flight on the map
  if (flights.length() > 1) {
    if (!plane.marker) {
      plane.marker = $(
          '<span class="badge plane_marker" ' +
              'style="background: ' + flight.color + ';">' +
          (flight.additional['competition_id'] || '') +
          '</span>');

      $(map.getLayersByName('Flight')[0].div).append(plane.marker);
    }

    var pixel = map.getPixelFromLonLat(
        new OpenLayers.LonLat(fix_data['loc'].x, fix_data['loc'].y));
    plane.marker.css('left', (pixel.x - plane.marker.outerWidth() / 2) + 'px');
    plane.marker.css('top', (pixel.y - 40) + 'px');

    plane.marker.show();
  }
}

function hidePlaneOnMap(flight) {
  var layer = map.getLayersByName('Flight')[0];

  var plane = flight.plane;

  layer.removeFeatures(plane);

  if (plane && plane.marker)
    plane.marker.hide();
}

function hideAllPlanesOnMap() {
  var layer = map.getLayersByName('Flight')[0];

  flights.each(function(flight) {
    var plane = flight.plane;

    layer.removeFeatures(plane);
    if (plane && plane.marker)
      plane.marker.hide();
  });
}


/**
 * Handles the mouseover events over the map to display near airplanes
 */
function hoverMap() {
  // search on every mousemove over the map viewport. Run this function only
  // every 25ms to save some computing power.
  var running = false;
  map.events.register('mousemove', null, function(e) {
    if (!map.hover_enabled)
      return;

    // call this function only every 25ms, else return early
    if (running) return;
    running = true;
    setTimeout(function() { running = false; }, 25);

    // create bounding box in map coordinates around mouse cursor
    var pixel = e.xy.clone();
    var hoverTolerance = 15;
    var llPx = pixel.add(-hoverTolerance / 2, hoverTolerance / 2);
    var urPx = pixel.add(hoverTolerance / 2, -hoverTolerance / 2);
    var ll = map.getLonLatFromPixel(llPx);
    var ur = map.getLonLatFromPixel(urPx);
    var loc = map.getLonLatFromPixel(pixel);

    // search for a aircraft position within the bounding box
    var nearest = searchForPlane(new OpenLayers.Bounds(
        ll.lon, ll.lat, ur.lon, ur.lat), loc, hoverTolerance);

    // if there's a aircraft within the bounding box, show the plane icon
    // and draw a position marker on the linechart.
    if (nearest != null) {
      // calculate time
      var flight = nearest.flight;
      var time_prev = flight.t[nearest.from];
      var time_next = flight.t[nearest.from + 1];
      var time = time_prev + (time_next - time_prev) * nearest.along;

      // set the map time to x
      setTime(time);
    } else {
      // hide everything
      setTime(default_time);
    }
  });
}


/**
 * Searches for the nearest aircraft position in mouse range
 *
 * @param {OpenLayers.Bounds} within Bounds to search within.
 * @param {OpenLayers.Point} loc Location of mouse click.
 * @param {Int} hoverTolerance Tolerance in pixel to search.
 * @return {Object} An object with the nearest flight.
 */
function searchForPlane(within, loc, hoverTolerance) {
  var possible_solutions = [];

  // circle throu all flights visible in viewport
  flights.each(function(flight) {
    var geometries = flight.geo.partitionedGeometries;
    var geometriesLength = geometries.length;

    for (var j = 0; j < geometriesLength; ++j) {
      var components = geometries[j].components;
      var componentsLength = components.length;

      for (var k = 1; k < componentsLength; ++k) {
        // check if the current vector between two points intersects our
        // "within" bounds if so, process this vector in the next step
        // (possible_solutions)
        var vector = new OpenLayers.Bounds();
        vector.bottom = Math.min(components[k - 1].y,
                                 components[k].y);
        vector.top = Math.max(components[k - 1].y,
                              components[k].y);
        vector.left = Math.min(components[k - 1].x,
                               components[k].x);
        vector.right = Math.max(components[k - 1].x,
                                components[k].x);

        if (within.intersectsBounds(vector))
          possible_solutions.push({
            from: components[k - 1].originalIndex,
            to: components[k].originalIndex,
            flight: flight
          });
      }
    }
  });

  // no solutions found. return.
  if (possible_solutions.length == 0)
    return null;

  // calculate map resolution (meters per pixel) at mouse location
  var loc_epsg4326 = loc.clone().transform(
      map.getProjectionObject(), WGS84_PROJ);
  var resolution = map.getResolution() * Math.cos(
      Math.PI / 180 * loc_epsg4326.lat);

  // find nearest distance between loc and vectors in possible_solutions
  var nearest, distance = Math.pow(hoverTolerance * resolution, 2);

  var possible_solutionsLength = possible_solutions.length;
  for (var i = 0; i < possible_solutionsLength; ++i) {
    var possible_solution = possible_solutions[i];
    var flight = possible_solution.flight;
    var components = flight.geo.components;

    for (var j = possible_solution.from + 1; j <= possible_solution.to; ++j) {
      var distToSegment = distanceToSegmentSquared({
        x: loc.lon,
        y: loc.lat
      }, {
        x1: components[j - 1].x,
        y1: components[j - 1].y,
        x2: components[j].x,
        y2: components[j].y
      });

      if (distToSegment.distance < distance) {
        distance = distToSegment.distance;
        nearest = {
          from: j - 1,
          to: j,
          along: distToSegment.along,
          flight: possible_solution.flight
        };
      }
    }
  }

  return nearest;
}


/**
 * (OpenLayers.Geometry.)distanceToSegmentSquared modified to return along, too.
 *
 * @param {Object} point An object with x and y properties representing the
 *     point coordinates.
 * @param {Object} segment An object with x1, y1, x2, and y2 properties
 *     representing endpoint coordinates.
 * @return {Object} An object with distance (squared) and along.
 */
distanceToSegmentSquared = function(point, segment) {
  var x0 = point.x;
  var y0 = point.y;
  var x1 = segment.x1;
  var y1 = segment.y1;
  var x2 = segment.x2;
  var y2 = segment.y2;
  var dx = x2 - x1;
  var dy = y2 - y1;
  var along = ((dx * (x0 - x1)) + (dy * (y0 - y1))) /
              (Math.pow(dx, 2) + Math.pow(dy, 2));
  var x, y;
  if (along <= 0.0) {
    x = x1;
    y = y1;
    along = 0;
  } else if (along >= 1.0) {
    x = x2;
    y = y2;
    along = 1;
  } else {
    x = x1 + along * dx;
    y = y1 + along * dy;
  }

  return {
    distance: Math.pow(x - x0, 2) + Math.pow(y - y0, 2),
    along: along
  };
};


/**
 * @param {DOMElement} placeholder DOM element of the phases table.
*/
function initPhasesTable(placeholder) {
  phase_table = slPhaseTable(placeholder);

  $(phase_table).on('selection_changed', function(event, data) {
    clearPhaseMarkers();

    if (data) {
      highlightFlightPhase(data.start, data.end);
      baro.setTimeHighlight(data.start, data.end);
    } else {
      baro.clearTimeHighlight();
    }

    baro.draw();
  });

  phases_layer = new OpenLayers.Layer.Vector('Flight Phases', {
    displayInLayerSwitcher: false
  });
  map.addLayer(phases_layer);
}


function clearPhaseMarkers() {
  phases_layer.removeAllFeatures();
}


function addPhaseMarker(lonlat, image_url) {
  var point = new OpenLayers.Geometry.Point(lonlat[1], lonlat[0]);
  point = point.transform(WGS84_PROJ, map.getProjectionObject());

  var feature = new OpenLayers.Feature.Vector(point, {}, {
    externalGraphic: image_url,
    graphicHeight: 21,
    graphicWidth: 16,
    graphicXOffset: -8,
    graphicYOffset: -21
  });

  phases_layer.addFeatures(feature);
}


function highlightFlightPhase(start, end) {
  // the phases table should contain only phases of our first flight only
  var flight = flights.at(0);

  var start_index = getNextSmallerIndex(flight.t, start);
  var end_index = getNextSmallerIndex(flight.t, end);

  if (start_index >= end_index) return;

  // collect bounding box of flight
  var bounds = new OpenLayers.Bounds();
  for (var i = start_index; i <= end_index; ++i)
    bounds.extendXY(flight.lonlat[i][1], flight.lonlat[i][0]);

  bounds.transform(WGS84_PROJ, map.getProjectionObject());
  map.zoomToExtent(bounds.scale(2));

  addPhaseMarker(flight.lonlat[start_index],
      '/vendor/openlayers/img/marker-green.png');

  addPhaseMarker(flight.lonlat[end_index],
      '/vendor/openlayers/img/marker.png');
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
    var coordinates = flight.geo.components[flight.geo.components.length - 1];
    map.panTo(new OpenLayers.LonLat(coordinates.x, coordinates.y));
  }
}
