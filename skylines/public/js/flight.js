/**
 * flights
 *
 * Array of flight objects. (see addFlight method)
 */
var flights = [];

var flot;

var highlighted_flight_sfid;

/**
 * colors
 *
 * List of colors for flight path display
 */
//var colors = ['#bf2fa2', '#2f69bf', '#d63a35', '#d649ff'];
var colors = ['#004bbd', '#bf0099', '#cf7c00', '#ff0000', '#00c994', '#ffff00'];
var contest_colors = {'olc_plus classic': '#ff2c73',
                      'olc_plus triangle': '#9f14ff'}

/**
 * Function initOpenLayers
 *
 * Initialize the map and add airspace and flight path layers.
 */

function initFlightLayer() {
  var default_style = new OpenLayers.Style({
    strokeColor: "${color}",
    strokeWidth: 2,
    graphicZIndex: 1000
  });

  var contest_style = new OpenLayers.Style({
    strokeColor: "${color}",
    strokeWidth: 2,
    strokeDashstyle: "dash",
    graphicZIndex: 1500
  });

  var plane_style = new OpenLayers.Style({
    // Set the external graphic and background graphic images.
    externalGraphic: "${getGraphic}",
    // Makes sure the background graphic is placed correctly relative
    // to the external graphic.
    graphicXOffset: -(40/2),
    graphicYOffset: -8,
    graphicWidth: 40,
    graphicHeight: 24,
    rotation: "${rotation}",
    // Set the z-indexes of both graphics to make sure the background
    // graphics stay in the background (shadows on top of markers looks
    // odd; let's not do that).
    graphicZIndex: 2000
  }, {
    context: {
      getGraphic: function(feature) {
        var msie_8 = $.browser.msie && (parseInt($.browser.version, 10) < 9);
        var ghost_glider = msie_8?"/images/glider_symbol_ghost_msie.png":"/images/glider_symbol_ghost.png";
        var normal_glider = msie_8?"/images/glider_symbol_msie.png":"/images/glider_symbol.png";
        return feature.attributes["ghost"]?ghost_glider:normal_glider;
      }
    }
  });

  var hidden_style = new OpenLayers.Style({
    display: 'none'
  });

  var flightPathLayer = new OpenLayers.Layer.Vector("Flight", {
    styleMap: new OpenLayers.StyleMap({
      'default': default_style,
      'contest': contest_style,
      'plane': plane_style,
      'hidden': hidden_style
    }),
    rendererOptions: {
        zIndexing: true
    }
  });

  map.addLayer(flightPathLayer);

  map.events.register("move", this, function() {
    initRedrawLayer(flightPathLayer);
  });

  map.events.register("moveend", this, updateFlotScale);
};

function updateFlotScale() {
  var first_t = 999999;
  var last_t = 0;

  // circle throu all flights
  for (var fid = 0; fid < flights.length; fid++) {
    var flight = flights[fid];

    // if flight is not in viewport continue.
    if (flight.geo.partitionedGeometries.length == 0)
      continue;

    // show barogram of all trace parts visible
    var length = flight.geo.partitionedGeometries.length;
    var comp_length = flight.geo.partitionedGeometries[length-1].components.length;
    var first = flight.geo.partitionedGeometries[0].components[0].originalIndex;
    var last = flight.geo.partitionedGeometries[length-1].components[comp_length-1].originalIndex;

    // get first and last time which should be the bounds of the barogram
    if (flight.t[first] < first_t)
      first_t = flight.t[first];

    if (flight.t[last] > last_t)
     last_t = flight.t[last];
  }

  var opt = flot.getOptions();
  opt.yaxes[0].min = opt.yaxes[0].max = null;
  if (last_t == 0) {
    opt.xaxes[0].min = opt.xaxes[0].max = null;
  } else {
    opt.xaxes[0].min = first_t * 1000;
    opt.xaxes[0].max = last_t * 1000;
  }

  flot.setupGrid();
  flot.draw();
}

/**
 * Function: initRedrawLayer
 *
 * initiates the redraw of a layer
 */
function initRedrawLayer(layer) {
  // Run this function only every 50ms to save some computing power.
  if (this.initRedrawLayerRunning) return;

  this.initRedrawLayerRunning = true;
  setTimeout(function() { this.initRedrawLayerRunning = false; }, 50);

  layer.redraw();
};

/**
 * Function: addFlight
 *
 * Add a flight to the map and barogram.
 *
 * Parameters:
 * sfid - {int} SkyLines flight ID
 * _lonlat - {String} Google polyencoded string of geolocations (lon + lat, WSG 84)
 * _levels - {String} Google polyencoded string of levels of detail
 * _num_levels - {int} Number of levels encoded in _lonlat and _levels
 * _time - {String} Google polyencoded string of time values
 * _height - {String} Google polyencoded string of height values
 * _enl - {String} Google polyencoded string of engine noise levels
 * zoom_levels - {Array(double)} Array of zoom levels where to switch between the LoD.
 * _contests - {Array(Objects)} Array of scored/optimised contests
 *   Such an object must contain: name, turnpoints, times
 *   turnpoints and times are googlePolyEncoded strings.
 * _additional - {Object(String)} May contain additional information about the flight,
 *   e.g. registration number, callsign...
 *
 * Note: _lonlat, _levels, _time, _enl, and _height MUST have the same number of elements when decoded.
 */

function addFlight(sfid, _lonlat, _levels, _num_levels, _time, _height, _enl, zoom_levels, _contests, _additional) {
  var height = OpenLayers.Util.decodeGoogle(_height);
  var time = OpenLayers.Util.decodeGoogle(_time);
  var enl = OpenLayers.Util.decodeGoogle(_enl);
  var lonlat = OpenLayers.Util.decodeGooglePolyline(_lonlat);
  var lod = OpenLayers.Util.decodeGoogleLoD(_levels, _num_levels);

  var points = new Array();
  for (var i = 0, len = lonlat.length; i < len; i++) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i].lon, lonlat[i].lat).
      transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()));
  }

  // add new flight
  var flight = new OpenLayers.Geometry.ProgressiveLineString(points, lod, zoom_levels);
  flight.clip = 1;

  var color = colors[flights.length%colors.length];
  var feature = new OpenLayers.Feature.Vector(flight, { color: color });

  var plane = new OpenLayers.Feature.Vector(
    new OpenLayers.Geometry.Point(lonlat[0].lon, lonlat[0].lat).
      transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()),
    { rotation: 0 }
  );
  plane.renderIntent = 'plane';

  map.getLayersByName("Flight")[0].addFeatures([feature, plane]);

  var contests = [];
  if (_contests) {
    for (var i = 0; i < _contests.length; i++) {
      var turnpoints = OpenLayers.Util.decodeGooglePolyline(_contests[i].turnpoints);
      var times = OpenLayers.Util.decodeGoogle(_contests[i].times);

      contests.push({
        name: _contests[i].name,
        turnpoints: turnpoints,
        times: times,
        visible: true // this is only valid for the contests of this flight.
      });

      addContest(_contests[i].name, turnpoints, times, true, sfid);
    }
  }

  var flot_h = [], flot_enl = [];
  for (var i = 0; i < time.length; i++) {
      var timestamp = time[i] * 1000;
      flot_h.push([timestamp, convert_altitude(height[i])]);
      flot_enl.push([timestamp, enl[i]]);
  }

  var table_row = $(
    "<tr>" +
    "<td><span class=\"badge\" style=\"background: " + color + ";\">" +
      (_additional && _additional['competition_id']?_additional['competition_id']:"") +
    "</span></td>" +
    "<td>--:--:--</td>" +
    "<td>--</td>" +
    "<td>--</td>" +
    "<td>--</td>" +
    "</tr>");


  table_row.bind('hover', function(e) {
    if (flights.length > 1)
      $(this).css("cursor", "pointer");
  });

  table_row.bind('click', function(e) {
    if (flights.length <= 1)
      return;

    if (highlighted_flight_sfid == sfid)
      clearHighlight();
    else
      setHighlight(sfid);
  });

  $("#fix-data").append(table_row);

  flights.push({
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
    table_row: table_row,
    flot_h: flot_h,
    flot_enl: flot_enl,
    additional: _additional?_additional:null
  });

  updateFlotData();
  updateFlotScale();
};

/**
 * Function: addFlightFromJSON
 *
 * Parameters:
 * url - {string} URL to fetch
 */
function addFlightFromJSON(url) {
  $.ajax(url,{
    success: function(data) {
      for (var flight_id = 0; flight_id < flights.length; flight_id++) {
        if (flights[flight_id].sfid == data.sfid) return;
      }

      addFlight(data.sfid, data.encoded.points, data.encoded.levels,
                data.num_levels, data.barogram_t, data.barogram_h,
                data.enl, data.zoom_levels, data.contests, data.additional);

      initRedrawLayer(map.getLayersByName("Flight")[0]);
    }
  });
};


/**
 * Function: addContest
 *
 * Add a flight contest trace to the map
 *
 * Parameters:
 * name - {String} Name to display
 * lonlat - {Array(Object)} Array of LonLat pairs
 * times - {Array(Integer)} Array of times
 * visible - {Bool} Flag weather to show the trace or not
 * sfid - {Integer} The SkyLines flight id this contest trace belongs to
 */
function addContest(name, lonlat, times, visible, sfid) {
  var points = new Array();
  for (var i = 0, len = lonlat.length; i < len; i++) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i].lon, lonlat[i].lat).
      transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()) );
  }

  var trace = new OpenLayers.Geometry.LineString(points);

  var color = contest_colors[name] || '#ff2c73';
  var feature = new OpenLayers.Feature.Vector(trace, {
    color: color,
    sfid: sfid
  });

  // show the contest traces only for the first flight by default
  feature.renderIntent = (flights.length == 0) ? 'contest' : 'hidden';

  map.getLayersByName("Flight")[0].addFeatures(feature);
}

/**
 * Function: getAllFlightsBounds
 *
 * Returns:
 * {OpenLayers.Bounds} - bounds containing all flights on the map.
 */

function getAllFlightsBounds() {
  var bounds = new OpenLayers.Bounds();

  for (var fid = 0; fid < flights.length; fid++) {
    bounds.extend(flights[fid].geo.bounds);
  }

  return bounds;
};


/**
 * Function: getNextSmallerIndex
 *
 * Searches the next smaller index to a number in a monotonic array
 *
 * Parameters:
 * a - {Array} Array
 * n - {double} Number
 *
 * Returns:
 * {int} Index next smaller to Number in Array
 */
function getNextSmallerIndex(a, n) {
  var l = a.length;

  if (l < 2)
    return l - 1;

  for (l; --l;) {
    if (a[l] < n) break;
  }

  return l;
}


/**
 * Function: formatSecondsAsTime
 *
 * Parameters:
 * seconds - {int} Seconds of day
 *
 * Returns:
 * {String} formatted time "HH:MM:SS"
 */

function formatSecondsAsTime(seconds) {
  seconds %= 86400;
  var h = Math.floor(seconds/3600);
  var m = Math.floor((seconds%3600)/60);
  var s = Math.floor(seconds%3600%60);

  return pad(h,2) + ":" + pad(m,2) + ":" + pad(s,2); // Format the result into time strings
}

function initFlot(element) {
  flot = $.plot(element, [], {
      grid: {
        borderWidth: 0,
        hoverable: true,
        autoHighlight: false,
        margin: 5
      },
      xaxis: {
        mode: "time",
        timeformat: "%H:%M"
      },
      yaxes: [{
        tickFormatter: add_altitude_unit
        }, {
        show: false,
        min: 0,
        max: 1000
      }],
      crosshair: {
        mode: "x"
      }
  });

  var mouse_container_running = false;
  element.bind('plothover', function(event, pos, item) {
    if (mouse_container_running)
      return;

    mouse_container_running = true;

    setTimeout(function() {
      mouse_container_running = false;
    }, 25);

    setTime(pos.x / 1000);
  }).bind('mouseout', function(event) {
    setTime(null);
  });
}

function updateFlotData() {
  var highlighted = flightWithSFID(highlighted_flight_sfid);

  var data = [];
  for (var id = 0; id < flights.length; id++) {
    var flight = flights[id];

    // Don't draw highlighted flight yet because it should be on top
    if (highlighted && flight.sfid == highlighted.sfid)
      continue;

    var color = flight.color;
    if (highlighted)
      // Fade out line color if another flight is highlighted
      color = $.color.parse(color).add('a', -0.6).toString()

    series = {
        data: flight.flot_h,
        color: color
    };

    if (highlighted) {
        series.shadowSize = 0;
        series.lines = { lineWidth : 1 };
    }

    data.push(series);

    // Don't show other flight's ENL if a flight is highlighted
    if (!highlighted)
      data.push({
        data: flight.flot_enl,
        color: flight.color,
        lines: {
          lineWidth: 0,
          fill: 0.2
        },
        yaxis: 2
      });
  }

  if (highlighted) {
    data.push({
      data: highlighted.flot_h,
      color: highlighted.color
    });

    data.push({
      data: highlighted.flot_enl,
      color: highlighted.color,
      lines: {
        lineWidth: 0,
        fill: 0.2
      },
      yaxis: 2
    });
  }

  var options = flot.getOptions();
  var markings = [];

  var contests;
  if (flights.length == 1)
    contests = flights[0].contests;
  else if (highlighted)
    contests = highlighted.contests;

  if (contests) {
    for (var i = 0; i < contests.length; ++i) {
      var contest = contests[i];
      var times = contest.times;
      var color = contest_colors[contest.name];

      for (var j = 0; j < times.length; ++j) {
        var time = times[j] * 1000;
        markings.push({
          lineWidth: 1,
          color: color,
          xaxis: {
            from: time,
            to: time
          }
        });
      }
    }
  }

  options.grid.markings = markings;

  flot.setData(data);
  flot.setupGrid();
  flot.draw();
}

function setTime(time) {
  // remove plane icons from map
  hideAllPlanesOnMap();

  // if the mouse is not hovering over the barogram or any trail on the map
  if (!time) {
    // remove crosshair from barogram
    flot.clearCrosshair();

    // remove data from fix-data table
    clearFixDataTable();

    return;
  }

  if (time == -1) {
    // lock barogram crosshair at the end
    flot.lockCrosshair({x: 999999999});
  } else {
    // update barogram crosshair
    flot.lockCrosshair({x: global_time * 1000});
  }

  for (var id = 0; id < flights.length; id++) {
    // calculate fix data
    fix_data = getFixData(id, time);
    if (!fix_data) {
      // update map
      hidePlaneOnMap(id);

      // update fix-data table
      clearFixDataTableRow(id);
    } else {
      // update map
      setPlaneOnMap(id, fix_data);

      // update fix-data table
      updateFixDataTableRow(id, fix_data);
    }
  }
}

function getFixData(id, time) {
  var flight = flights[id];

  if (time == -1)
    time = flight.t[flight.t.length - 1];
  else if (time < flight.t[0] || time > flight.t[flight.t.length-1])
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

  fix_data["time"] = t_prev;

  var loc_prev = flights[id].lonlat[index];
  var loc_next = flights[id].lonlat[index + 1];

  var lon_prev = loc_prev.lon, lat_prev = loc_prev.lat;
  var lon_next = loc_next.lon, lat_next = loc_next.lat;

  var _loc_prev = new OpenLayers.Geometry.Point(lon_prev, lat_prev);
  _loc_prev.transform(new OpenLayers.Projection("EPSG:4326"),
                      map.getProjectionObject());
  var _loc_next = new OpenLayers.Geometry.Point(lon_next, lat_next);
  _loc_next.transform(new OpenLayers.Projection("EPSG:4326"),
                      map.getProjectionObject());

  fix_data["lon"] = lon_prev + (lon_next - lon_prev) * dt_rel;
  fix_data["lat"] = lat_prev + (lat_next - lat_prev) * dt_rel;

  fix_data["loc"] = new OpenLayers.Geometry.Point(fix_data["lon"], fix_data["lat"]);
  fix_data["loc"].transform(new OpenLayers.Projection("EPSG:4326"),
                            map.getProjectionObject());

  fix_data["heading"] = Math.atan2(_loc_next.x - _loc_prev.x,
                                   _loc_next.y - _loc_prev.y) * 180 / Math.PI;

  if (dt_total != 0)
    fix_data["speed"] = OpenLayers.Util.distVincenty(loc_next, loc_prev) * 1000 / dt_total;

  var h_prev = flights[id].h[index];
  var h_next = flights[id].h[index + 1];

  fix_data["alt-msl"] = h_prev;

  if (dt_total != 0)
    fix_data["vario"] = (h_next - h_prev) / dt_total;

  return fix_data;
}

function setPlaneOnMap(id, fix_data) {
  // set plane location
  flights[id].plane.geometry = fix_data["loc"];

  // set plane heading
  // <heading> in degrees
  flights[id].plane.attributes.rotation = fix_data["heading"];

  // add plane to map
  map.getLayersByName("Flight")[0].addFeatures(flights[id].plane);
}

function hidePlaneOnMap(id) {
  map.getLayersByName("Flight")[0].removeFeatures(flights[id].plane);
}

function hideAllPlanesOnMap() {
  var layer = map.getLayersByName("Flight")[0];
  for (var id = 0; id < flights.length; id++)
    layer.removeFeatures(flights[id].plane);
}

function updateFixDataTableRow(id, fix_data) {
  flights[id].table_row.find("td").each(function(index, cell) {
    switch (index) {
    case 0:
      return;
    case 1:
      var html = formatSecondsAsTime(fix_data["time"]);
      $(cell).html(html);
      break;
    case 2:
      var html = format_altitude(fix_data["alt-msl"]);
      $(cell).html(html);
      break;
    case 3:
      if (fix_data["vario"] !== undefined) {
        var html = format_lift(fix_data["vario"]);
        if (fix_data["vario"] >= 0)
          html = "+" + html;

        $(cell).html(html);
      } else {
        $(cell).html("--");
      }
      break;
    case 4:
      if (fix_data["speed"] !== undefined) {
        var html = format_speed(fix_data["speed"]);
        $(cell).html(html);
      } else {
        $(cell).html("--");
      }
      break;
    }
  });
}

function clearFixDataTableRow(id, fix_data) {
  flights[id].table_row.find("td").each(function(index, cell) {
    switch (index) {
    case 0:
      return;
    case 1:
      $(cell).html("--:--:--");
      break;
    default:
      $(cell).html("--");
      break;
    }
  });
}

function clearFixDataTable() {
  for (var id = 0; id < flights.length; id++)
    clearFixDataTableRow(id);
}

function flightWithSFID(sfid) {
  for (var id = 0; id < flights.length; id++) {
    var flight = flights[id];
    if (flight.sfid == sfid)
      return flight;
  }

  return null;
}

function clearHighlight(defer_update) {
  if (!highlighted_flight_sfid)
    return;

  // Find currently highlighted flight
  var flight = flightWithSFID(highlighted_flight_sfid);
  if (flight)
    // Removed table row styling for selected flight
    flight.table_row.removeClass("selected");

  // Unset the highlighted sfid variable
  highlighted_flight_sfid = undefined;

  // Unless specifically deferred update the barogram
  if (defer_update != true)
    updateFlotData();
}

function setHighlight(sfid) {
  if (highlighted_flight_sfid == sfid)
    return;

  // Clear the currently highlighted flight
  clearHighlight(true);

  // Find flight that should be highlighted now
  var flight = flightWithSFID(sfid);
  if (!flight)
    return;

  // Add table row styling
  flight.table_row.addClass("selected");

  // Save highlighted status
  highlighted_flight_sfid = sfid;

  // Update barogram
  updateFlotData();
}

/**
 * Function: hoverMap
 *
 * Handles the mouseover events over the map to display near airplanes
 */

function hoverMap() {
  // search on every mousemove over the map viewport. Run this function only
  // every 25ms to save some computing power.
  var running = false;
  map.events.register("mousemove", this, function(e) {
    // call this function only every 25ms, else return early
    if (running) return;
    running = true;
    setTimeout(function() { running = false; }, 25);

    // create bounding box in map coordinates around mouse cursor
    var pixel = e.xy.clone();
    var hoverTolerance = 15;
    var llPx = pixel.add(-hoverTolerance/2, hoverTolerance/2);
    var urPx = pixel.add(hoverTolerance/2, -hoverTolerance/2);
    var ll = map.getLonLatFromPixel(llPx);
    var ur = map.getLonLatFromPixel(urPx);
    var loc = map.getLonLatFromPixel(pixel);

    // search for a aircraft position within the bounding box
    var nearest = searchForPlane(new OpenLayers.Bounds(ll.lon, ll.lat, ur.lon, ur.lat), loc, hoverTolerance);

    // if there's a aircraft within the bounding box, show the plane icon and draw
    // a position marker on the linechart.
    if (nearest != null) {
      // calculate time
      var x = flights[nearest.fid].t[nearest.from] + (flights[nearest.fid].t[nearest.from+1]-flights[nearest.fid].t[nearest.from])*nearest.along;

      // set the map time to x
      setTime(x);
    } else {
      // hide everything
      setTime(null);
    }
  });
}

/**
 * Function: searchForPlane
 *
 * Searches for the nearest aircraft position in mouse range
 *
 * Parameters:
 * within - {OpenLayers.Bounds} Bounds to search within
 * loc - {OpenLayers.Point} Location of mouse click
 * hoverTolerance - {Int} Tolerance in pixel to search
 *
 * Returns:
 * {Object} An object with the nearest flight.
 */
function searchForPlane(within, loc, hoverTolerance) {
  var possible_solutions = [];

  // circle throu all flights visible in viewport
  for (var fid = 0; fid < flights.length; fid++) {
    var flight = flights[fid].geo;

    for (var part_geo = 0; part_geo < flight.partitionedGeometries.length; part_geo++) {
      var components = flight.partitionedGeometries[part_geo].components;

      for (var i = 1, len = components.length; i < len; i++) {
        // check if the current vector between two points intersects our "within" bounds
        // if so, process this vector in the next step (possible_solutions)
        var vector = new OpenLayers.Bounds();
        vector.bottom = Math.min(components[i-1].y,
                                 components[i].y);
        vector.top =  Math.max(components[i-1].y,
                               components[i].y);
        vector.left = Math.min(components[i-1].x,
                               components[i].x);
        vector.right = Math.max(components[i-1].x,
                                 components[i].x);

        if (within.intersectsBounds(vector))
          possible_solutions.push({
            from: components[i-1].originalIndex,
            to: components[i].originalIndex,
            fid: fid
          });
      }
    }
  }

  // no solutions found. return.
  if (possible_solutions.length == 0) return null;

  // calculate map resolution (meters per pixel) at mouse location
  var loc_epsg4326 = loc.clone().transform(map.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
  var resolution = map.getResolution() * Math.cos(Math.PI/180 * loc_epsg4326.lat);

  // find nearest distance between loc and vectors in possible_solutions
  var nearest, distance = Math.pow(hoverTolerance * resolution, 2);

  for (var i = 0; i < possible_solutions.length; i++) {
    for (var j = possible_solutions[i].from + 1; j <= possible_solutions[i].to; j++) {
      var distToSegment = distanceToSegmentSquared({x: loc.lon, y: loc.lat},
        { x1: flights[possible_solutions[i].fid].geo.components[j-1].x, y1: flights[possible_solutions[i].fid].geo.components[j-1].y,
          x2: flights[possible_solutions[i].fid].geo.components[j].x, y2: flights[possible_solutions[i].fid].geo.components[j].y });

      if (distToSegment.distance < distance) {
        distance = distToSegment.distance;
        nearest = { from: j-1, to: j, along: distToSegment.along, fid: possible_solutions[i].fid};
      }
    }
  }

  return nearest;
}


/**
 * Function: (OpenLayers.Geometry.)distanceToSegmentSquared
 * modified to return along, too.
 *
 * Parameters:
 * point - {Object} An object with x and y properties representing the
 *     point coordinates.
 * segment - {Object} An object with x1, y1, x2, and y2 properties
 *     representing endpoint coordinates.
 *
 * Returns:
 * {Object} An object with distance (squared) and along.
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
    if(along <= 0.0) {
        x = x1;
        y = y1;
        along = 0;
    } else if(along >= 1.0) {
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

