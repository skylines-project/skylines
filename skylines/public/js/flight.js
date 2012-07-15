/**
 * flights
 *
 * Array of flight objects. (see addFlight method)
 */
var flights = [];


/**
 * primary_flight
 *
 * Defines which flight should be handled first
 */
var primary_flight = 0;


/**
 * barogram
 *
 * Holds the Raphael instance
 */
var barogram;

/**
 * barogram_t, barogram_h and barogram_enl
 *
 * {Array(Array(double))} - contains time, height and enl values for the barogram.
 */
var barogram_t = [];
var barogram_h = [];
var barogram_enl = [];
var barogram_markers = [];


/**
 * colors
 *
 * List of colors for flight path display
 */
//var colors = ['#bf2fa2', '#2f69bf', '#d63a35', '#d649ff'];
var colors = ['#004bbd', '#bf0099', '#cf7c00', '#ff0000', '#00c994'];
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

  var flightPathLayer = new OpenLayers.Layer.Vector("Flight", {
    styleMap: new OpenLayers.StyleMap({
      'default': default_style,
      'contest': contest_style,
      'plane': plane_style
    }),
    rendererOptions: {
        zIndexing: true
    }
  });

  map.addLayer(flightPathLayer);

  map.events.register("move", this, function() {
    initRedrawLayer(flightPathLayer);
  });
};

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
 *
 * Note: _lonlat, _levels, _time, _enl, and _height MUST have the same number of elements when decoded.
 */

function addFlight(sfid, _lonlat, _levels, _num_levels, _time, _height, _enl, zoom_levels, _contests) {
  var height = OpenLayers.Util.decodeGoogle(_height);
  var time = OpenLayers.Util.decodeGoogle(_time);
  var enl = OpenLayers.Util.decodeGoogle(_enl);
  var lonlat = OpenLayers.Util.decodeGooglePolyline(_lonlat);
  var lod = OpenLayers.Util.decodeGoogleLoD(_levels, _num_levels);

  var points = new Array();
  for (var i = 0, len = lonlat.length; i < len; i++) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i].lon, lonlat[i].lat).
      transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()) );
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

  var contests = [],
      markers = [];
  for (i in _contests) {
    var turnpoints = OpenLayers.Util.decodeGooglePolyline(_contests[i].turnpoints);
    var times = OpenLayers.Util.decodeGoogle(_contests[i].times);

    contests.push({
      name: _contests[i].name,
      turnpoints: turnpoints,
      times: times,
      visible: true // this is only valid for the contests of this flight.
    });

    markers.push(addContest(_contests[i].name, turnpoints, times, true));
  }

  flights.push({
    lonlat: lonlat,
    t: time,
    h: height,
    enl: enl,
    geo: flight,
    color: color,
    plane: plane,
    sfid: sfid,
    index: 0,
    dx: 0,
    last_update: time[time.length - 1],
    contests: contests,
    markers: markers
  });

  var i = flights.length - 1;

  barogram_t.push(flights[i].t);
  barogram_h.push(flights[i].h);
  barogram_enl.push(flights[i].enl);
  barogram_markers.push(flights[i].markers);
  primary_flight = i;
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
      for (flight_id in flights) {
        if (flights[flight_id].sfid == data.sfid) return;
      }

      addFlight(data.sfid, data.encoded.points, data.encoded.levels,
                data.num_levels, data.barogram_t, data.barogram_h,
                data.enl, data.zoom_levels, data.contests);

      initRedrawLayer(map.getLayersByName("Flight")[0]);
      $.proxy(updateBarogram, { reset_y_axis: true })();
    }
  });
};


/**
 * Function: addContest
 *
 * Add a flight contest trace to the map and return
 * it's turnpoints as markers for the barogram.
 *
 * Parameters:
 * name - {String} Name to display
 * lonlat - {Array(Object)} Array of LonLat pairs
 * times - {Array(Integer)} Array of times
 * visible - {Bool} Flag weather to show the trace or not
 */
function addContest(name, lonlat, times, visible) {
  var points = new Array();
  for (var i = 0, len = lonlat.length; i < len; i++) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i].lon, lonlat[i].lat).
      transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()) );
  }

  var trace = new OpenLayers.Geometry.LineString(points);

  var color = contest_colors[name] || '#ff2c73';
  var feature = new OpenLayers.Feature.Vector(trace, { color: color });
  feature.renderIntent = 'contest';

  map.getLayersByName("Flight")[0].addFeatures(feature);

  var markers = [];
  for (var i = 0; i < times.length; i++) {
    markers.push({
      x: times[i],
      value: (i == 0) ? 'Start' : (i == times.length - 1) ? 'End' : 'TP ' + i,
      color: color
    });
  }

  return markers;
}

/**
 * Function: getAllFlightsBounds
 *
 * Returns:
 * {OpenLayers.Bounds} - bounds containing all flights on the map.
 */

function getAllFlightsBounds() {
  var bounds = new OpenLayers.Bounds();

  for (fid in flights) {
    bounds.extend(flights[fid].geo.bounds);
  }

  return bounds;
};


/**
 * Function: getNearestNumber
 *
 * Searches the closest index to a number in a monotonic array.
 *
 * Parameters:
 * a - {Array} Array
 * n - {double} Number
 *
 * Returns:
 * {int} Index closest to Number in the Array.
 */

//+ Carlos R. L. Rodrigues
//@ http://jsfromhell.com/array/nearest-number [rev. #0]
function getNearestNumber(a, n){
  if((l = a.length) < 2)
    return l - 1;
  for(var l, p = Math.abs(a[--l] - n); l--;)
    if(p < (p = Math.abs(a[l] - n)))
      break;
  return l + 1;
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


/**
 * Function: setIndexFromTime
 *
 * Set index and dx for the current time in each flight
 */
function setIndexFromTime(time) {
  for (fid in flights) {
    var flight = flights[fid];

    if (time < flight.t[0] || time > flight.t[flight.t.length-1]) {
      // out of range
      flight.dx = 0;
      flight.index = -1;
      continue;
    }

    var index = getNearestNumber(flight.t, time);

    if (time < flight.t[index] && (flight.t[index] - flight.t[index-1]) != 0) {
      flight.dx = (time - flight.t[index-1])/(flight.t[index] - flight.t[index-1]);
      flight.index = index - 1;
    } else if ((flight.t[index+1] - flight.t[index]) != 0) {
      flight.dx = (time - flight.t[index])/(flight.t[index+1] - flight.t[index]);
      flight.index = index;
    } else {
      flight.dx = 0;
      flight.index = index;
    }

    if (flight.index == flight.t.length - 1) {
      flight.index--;
      flight.dx = 1;
    }
  }
}


/**
 * Function: setFlightTime
 *
 * Set the map time.
 */
function setFlightTime(time) {
  // hide all planes
  hidePlanePosition();
  barogram.linechart.hoverColumn.position.hide();

  // find the position indexes of all flight available.
  setIndexFromTime(time);

  // set the primary flight
  setPrimaryFlight(primary_flight);

  // no flight found which is in range? return early, draw nothing.
  if (flights[primary_flight].index == -1) return;

  // interpolate current height of primary_flight
  var height = flights[primary_flight].h[flights[primary_flight].index] +
    (flights[primary_flight].h[flights[primary_flight].index+1] - flights[primary_flight].h[flights[primary_flight].index]) *
     flights[primary_flight].dx;

  // calculate y-position of position marker for current primary_flight and show marker
  var prop = barogram.linechart.getProperties();
  var rel_x = (time - prop.minx) * prop.kx + prop.x + prop.gutter;
  var rel_y = prop.y - (height - prop.miny) * prop.ky + prop.height - prop.gutter;
  barogram.linechart.hoverColumn(flights[primary_flight].index, rel_x, rel_y, primary_flight);

  // draw plane icons on map
  for (fid in flights) {
    // do not show plane if out of range.
    if (flights[fid].index == -1) continue;

    showPlanePosition(flights[fid].index, flights[fid].dx, fid, (fid!=primary_flight));
  }
}

/**
 * Function: setPrimaryFlight
 *
 * Sets the primary flight. Try to set it to primary, fallback to another flight
 *
 * Parameters:
 * primary - {Integer} primary flight
 */
function setPrimaryFlight(primary) {
  // we'd like to have an flight within the current range as primary_flight.
  if (flights[primary].index == -1) {
    // our current primary flight is out of range. find first flight in range...
    for (primary in flights) if (flights[primary].index != -1) break;
  }

  // the primary flight has changed...
  if (primary_flight != primary) {
    // update barogram and set primary_flight if it changed
    barogram.linechart.setPrimary(primary);
    primary_flight = primary;
  }
}

/**
 * Function: render_barogram
 *
 * Initialize Raphael Linechart, handle it's mouseover events.
 *
 * Parameters:
 * element - {Object} jQuery container object for barogram.
 */

function render_barogram(element) {
  // create Raphael instance and draw linechart.
  barogram = Raphael("barogram", "100%", "100%");
  var linechart = barogram.linechart(30, 0,
                      element.innerWidth() - 50, element.innerHeight() - 10,
                      barogram_t,
                      barogram_h,
                      { axis: "0 0 1 1",
                        axisxstep: 8,
                        axisxfunc: formatSecondsAsTime,
                        colors: colors,
                        width: 1.5,
                        stripes: {
                          y: barogram_enl,
                          height: element.innerHeight() - 30,
                          visible: !($.browser.msie && (parseInt($.browser.version, 10) < 9)) },
                        markers: barogram_markers });

  // create position marker and it's elements.
  var position = barogram.set().hide();

  var hoverLine = barogram.path().attr({
    stroke: '#a22',
    'stroke-width': 2
  }).hide();

  var text = barogram.text().hide();

  var textRect = barogram.rect().attr({
    fill: '#fff',
    opacity: .8,
    stroke: '#999',
    r: 3
  }).hide();

  var hoverCircle = barogram.circle().attr({
    stroke: '#a22',
    'stroke-width': 2,
    r: 6
  }).hide();

  position.push(hoverLine);
  position.push(hoverCircle);
  position.push(textRect.insertAfter(hoverCircle));
  position.push(text.insertAfter(textRect));

  // create mouse_container overlay over linechart. fixes some bugs in browsers
  // where no mouseout events where fired when the mouse leaves the linechart.
  var mouse_container = $("<div></div>");
  mouse_container.css({
    width: element.innerWidth(),
    height: element.innerHeight(),
    'top': 0,
    'left': 0,
    position: 'absolute',
    opacity: 0,
    'background-color': '#fff'
  });
  element.append(mouse_container);

  // add mousemove function.
  // Run this function only every 25ms to save some computing power.
  var mouse_container_running = false;
  mouse_container.mousemove(function(e) {
    // call this function only every 25ms, else return early
    if (mouse_container_running) return;
    mouse_container_running = true;
    setTimeout(function() { mouse_container_running = false; }, 25);

    var prop = linechart.getProperties();
    var kx_inv = 1 / prop.kx;
    var rel_x = e.clientX - mouse_container.offset().left;
    var x = prop.minx + (rel_x - prop.x - prop.gutter) * kx_inv;
    if (x < prop.minx || x > prop.maxx) return;

    // set the map time to x
    setFlightTime(x);
  });

  // hide everything on mouse out
  mouse_container.mouseout(function(e) {
    hidePlanePosition();
    position && position.hide();
  });

  var enl_label = $("<span>ENL</span>");
  enl_label.css({
    'top': 5,
    'right': 2,
    position: 'absolute',
    color: linechart.getStripesState() ? '#ffbf29' : '#aaa',
    'font-weight': 'bold',
    cursor: 'pointer'
  }).tooltip({
    placement: 'left',
    title: 'Click to toggle ENL display'
  }).click(function(e) {
    linechart.toggleStripes();
    $(this).css({ color: linechart.getStripesState() ? '#ffbf29' : '#aaa' });
  });
  element.append(enl_label);

  // update the position marker at index in flight fid. x and y are relative to the linechart viewport.
  var hoverColumn = function(index, x, y, fid) {
    position.toFront();
    var attrs = linechart.getProperties();

    hoverLine.attr({ path:
      "M " + x.toString() + " " + attrs.height + " " +
      "l 0 " + (-(attrs.height - y) + 6).toString() +
      "M " + x.toString() + " 0 " +
      "l 0 " + (y - 6).toString()
    });

    hoverCircle.attr({
      cx: x,
      cy: y
    });

    var vario = null;
    if (flights[fid].t[index+1] != undefined) {
      vario = (flights[fid].h[index+1] - flights[fid].h[index]) / (flights[fid].t[index+1] - flights[fid].t[index]);
    }

    var speed = null;
    if (flights[fid].t[index+1] != undefined) {
      speed = OpenLayers.Util.distVincenty(flights[fid].lonlat[index+1], flights[fid].lonlat[index]);
      speed *= 1000;
      speed /= (flights[fid].t[index+1] - flights[fid].t[index]);
    }

    text.attr({
      x: x,
      y: attrs.height - 20,
      text: Math.round(flights[fid].h[index]) + " m" +
            ((vario !== null)?"\n" + (Math.round(vario*10)/10) + " m/s":"") +
            ((speed !== null)?"\n" + (Math.round(speed*3.6*10)/10) + " km/h":"") +
            "\n" + formatSecondsAsTime(flights[fid].t[index + ((flights[fid].dx>=1)?1:0)])
    });

    textRect.attr({
      x: x - 60/2,
      y: attrs.height - 20 - 54/2,
      width: 60,
      height: 54
    });
/*
    var textBBox = text.getBBox();
    textRect.attr({
      x: textBBox.x - 2,
      y: textBBox.y - 2,
      width: textBBox.width + 4,
      height: textBBox.height + 4
    });
*/
    position.show();
  };

  hoverColumn.position = position;
  linechart.hoverColumn = hoverColumn;
  barogram.linechart = linechart;

  $(window).resize(function() {
    var attrs = linechart.getProperties();
    if (element.innerWidth() - 50 != attrs.width ||
        element.innerHeight() - 10 != attrs.height) {
      linechart.resetSize(element.innerWidth() - 50, element.innerHeight() - 10);
      mouse_container.css({
        width: element.innerWidth(),
        height: element.innerHeight(),
      });
    }
  });
}


/**
 * Function: showPlanePosition
 *
 * Show a aircraft icon on the map.
 *
 * Parameters:
 * id - {int} index of vector where the aircraft is
 * dx - {double} delta between id and id+1 to draw aircraft
 * fid - {int} flight id to use
 */

function showPlanePosition(id, dx, fid, ghost) {

  flights[fid].plane.attributes.rotation = 180/Math.PI *
    Math.atan2(flights[fid].lonlat[id+1].lon-flights[fid].lonlat[id].lon,
               flights[fid].lonlat[id+1].lat-flights[fid].lonlat[id].lat);

  var lon = flights[fid].lonlat[id].lon + (flights[fid].lonlat[id+1].lon - flights[fid].lonlat[id].lon)*dx;
  var lat = flights[fid].lonlat[id].lat + (flights[fid].lonlat[id+1].lat - flights[fid].lonlat[id].lat)*dx;

  flights[fid].plane.attributes.ghost = ghost?true:false;
  flights[fid].plane.geometry = new OpenLayers.Geometry.Point(lon, lat).
    transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());

  map.getLayersByName("Flight")[0].addFeatures(flights[fid].plane);
}


/**
 * Function: hidePlanePosition
 *
 * Hides all aircrafts drawn on the map
 */

function hidePlanePosition() {
  for (fid in flights) {
    map.getLayersByName("Flight")[0].removeFeatures(flights[fid].plane);
  }
}


/**
 * Function: scaleBarogram
 *
 * Scale the linechart according to the visible flight tracks on the map
 */

function scaleBarogram() {
  // update barogram linechart whenever the map has been moved.
  map.events.register("moveend", this, updateBarogram);
}

function updateBarogram(e) {
  var linechart = barogram.linechart;
  var reset_y_axis = this.reset_y_axis || false;

  var largest_partition = null;
  var total_first = [];
  var total_last = [];
  var first_t = 999999;
  var last_t = 0;

  // circle throu all flights
  for (fid in flights) {
    var flight = flights[fid];

    last = flight.t.length - 1;

    // if flight is not in viewport continue.
    if (flight.geo.partitionedGeometries.length == 0) continue;

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

  // is there any flight in our viewport?
  var none_in_range = true;

  for (fid in flights) {
    // get indices of flight path between first_t(ime) and last_t(ime)
    first = getNearestNumber(flights[fid].t, first_t);
    last = getNearestNumber(flights[fid].t, last_t);

    if (flights[fid].t[first] > last_t || flights[fid].t[last] < first_t) {
      // current flight is out of range. don't show it in barogram...
      total_first.push(-1);
      total_last.push(-1);
    } else {
      total_first.push(first);
      total_last.push(last);
      none_in_range = false;
    }
  }

  if (none_in_range)
    // reset linechart zoom when no flight is visible in viewport
    linechart.zoomReset(reset_y_axis);
  else
    // zoom linechart
    linechart.zoomInto(total_first, total_last, reset_y_axis);
};


/**
 * Function: hoverMap
 *
 * Handles the mouseover events over the map to display near airplanes
 */

function hoverMap() {
  var linechart = barogram.linechart;

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
    var nearest = searchForPlane(new OpenLayers.Bounds(ll.lon, ll.lat, ur.lon, ur.lat), loc);

    // if there's a aircraft within the bounding box, show the plane icon and draw
    // a position marker on the linechart.
    if (nearest !== null) {
      // calculate time
      var prop = linechart.getProperties();
      var x = flights[nearest.fid].t[nearest.from] + (flights[nearest.fid].t[nearest.from+1]-flights[nearest.fid].t[nearest.from])*nearest.along;

      // we expect the currently hovered flight is the top flight.
      setPrimaryFlight(nearest.fid);

      // set the map time to x
      setFlightTime(x);
    } else {
      // hide everything
      hidePlanePosition();
      linechart.hoverColumn.position.hide();
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
 *
 * Returns:
 * {Object} An object with the nearest flight.
 */
function searchForPlane(within, loc) {
  var possible_solutions = [];

  // circle throu all flights visible in viewport
  for (fid in flights) {
    var flight = flights[fid].geo;

    for (part_geo in flight.partitionedGeometries) {
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

  // find nearest distance between loc and vectors in possible_solutions
  var nearest, distance = 99999999999;
  for (i in possible_solutions) {
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

