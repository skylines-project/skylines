

/**
 * Array of flight objects. (see addFlight method)
 */
var flights = slFlightCollection();

var map;
var baro;
var fix_table;
var styles;

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

  flight = slFlight(sfid, _lonlat, _time, _height, _enl,
                    _contests, _elevations_t, _elevations_h, opt_additional);
  flights.add(flight);

  flight.setColor(opt_additional.color ||
                  colors[(flights.length() - 1) % colors.length]);

  var feature = new ol.Feature({
    geometry: flight.getGeometry(),
    sfid: flight.getID(),
    color: flight.getColor(),
    type: 'flight'
  });

  flights.getSource().addFeature(feature);

  flight.getContests().forEach(function(contest) {
    addContest(contest.name, contest.turnpoints,
               contest.times, flight.getID());
  });

  // Add flight as a row to the fix data table
  fix_table.addRow(flight.getID(), flight.getColor(),
                   flight.getCompetitionID());

  updateBaroData();
  updateBaroScale();
  baro.draw();

  $('#wingman-table').find('*[data-sfid=' + flight.getID() + ']')
      .find('.color-stripe').css('background-color', flight.getColor());

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
  if (flights.at(0).getID() == sfid)
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
      if (flight.getStartTime() < start_time)
        start_time = flight.getStartTime();
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
    if (flight.getEndTime() > stop_time)
      stop_time = flight.getEndTime();
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
      data: flight.getFlotHeight(),
      color: flight.getColor()
    };

    var enl_data = {
      data: flight.getFlotENL(),
      color: flight.getColor()
    };

    if (fix_table.getSelection() &&
        flight.getID() != fix_table.getSelection()) {
      passive.push(data);
    } else {
      active.push(data);
      enls.push(enl_data);
    }

    // Save contests of highlighted flight for later
    if (fix_table.getSelection() &&
        flight.getID() == fix_table.getSelection()) {
      contests = flight.getContests();
      elevations = flight.getFlotElev();
    }

    // Save contests of only flight for later if applicable
    if (flights.length() == 1) {
      contests = flight.getContests();
      elevations = flight.getFlotElev();
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
      var fix_data = flight.getFixData(time);
      if (!fix_data) {
        // update map
        hidePlaneOnMap(flight);

        // update fix-data table
        fix_table.clearFix(flight.getID());
      } else {
        // update map
        setPlaneOnMap(flight, fix_data);

        // update fix-data table
        fix_table.updateFix(flight.getID(), fix_data);
      }
    });
  }

  map.render();
  fix_table.render();
}

function setPlaneOnMap(flight, fix_data) {
  var plane = flight.getPlane();

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
              'background: ' + flight.getColor() + ';">' +
          (flight.getCompetitionID() || '') +
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
  var plane = flight.getPlane();

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
      var plane = flight.getPlane();
      if (plane.point !== null) {
        style.setRotation(plane['heading']);
        vector_context.setImageStyle(style);
        vector_context.drawPointGeometry(plane.point);
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
 * Moves the map to the last fix of a flight
 *
 * @param {int} sfid SkyLines flight ID.
 */
function followFlight(sfid) {
  if (!sfid) return;

  var flight = flights.get(sfid);
  if (flight) {
    var coordinate = flight.getGeometry().getLastCoordinate();

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
