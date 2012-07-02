/**
 * flights
 *
 * Array of flight objects. (see addFlight method)
 */
var flights = [];


/**
 * top_flight
 *
 * Defines which flight should be handled first
 */
var top_flight = 0;


/**
 * barogram
 *
 * Holds the Raphael instance
 */
var barogram;

/**
 * barogram_t and barogram_h
 *
 * {Array(Array(double))} - contains time and height values for the barogram.
 */
var barogram_t = [];
var barogram_h = [];


/**
 * colors
 *
 * List of colors for flight path display
 */
//var colors = ['#bf2fa2', '#2f69bf', '#d63a35', '#d649ff'];
var colors = ['#004bbd', '#bf0099', '#cf7c00', '#ff0000', '#00c994'];

/**
 * Function initOpenLayers
 *
 * Initialize the map and add airspace and flight path layers.
 */

function initFlightLayer() {
  var default_style = new OpenLayers.Style({
    strokeColor: "${color}",
    strokeWidth: 2
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
      'plane': plane_style
    })
  });

  map.addLayer(flightPathLayer);

  var initRedrawLayer = function(layer) {
    if (this.timer)
      return;

    this.timer = window.setTimeout(function() {
      this.timer = null; layer.redraw();
    }, 50);
  };

  map.events.register("move", this, function() {
    initRedrawLayer(flightPathLayer);
  });
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
 * zoom_levels - {Array(double)} Array of zoom levels where to switch between the LoD.
 *
 * Note: _lonlat, _levels, _time and _height MUST have the same number of elements when decoded.
 */

function addFlight(sfid, _lonlat, _levels, _num_levels, _time, _height, zoom_levels) {
  var height = OpenLayers.Util.decodeGoogle(_height);
  var time = OpenLayers.Util.decodeGoogle(_time);
  var lonlat = OpenLayers.Util.decodeGooglePolyline(_lonlat);
  var lod = OpenLayers.Util.decodeGoogleLoD(_levels, _num_levels);

  var points = new Array();
  for (var i = 0, len = lonlat.length; i < len; i++) {
    points.push(new OpenLayers.Geometry.Point(lonlat[i].lon, lonlat[i].lat).
      transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()) );
  }

  // check if the SkyLines flight id is already shown
  var update = -1;
  for (fid in flights) {
    if (sfid == flights[fid].sfid)
      update = fid;
  }

  if (update != -1) {
    // update flight
    var flight = flights[update];

    flight.geo.components = points;
    flight.geo.componentsLevel = lod;
    flight.t = time;
    flight.h = height;
    flight.lonlat = lonlat;

    // recalculate bounds
    flight.geo.bounds = flight.geo.calculateBounds();
    // reset indices
    for (var i = 0, len = flight.geo.components.length; i < len; i++) {
      flight.geo.components[i].originalIndex = i;
    }

    barogram_t[fid] = time;
    barogram_h[fid] = height;

  } else {
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

    flights.push({
      lonlat: lonlat,
      t: time,
      h: height,
      geo: flight,
      color: color,
      plane: plane,
      sfid: sfid,
      index: 0,
      dx: 0
    });

    var i = flights.length - 1;

    barogram_t.push(flights[i].t);
    barogram_h.push(flights[i].h);
    top_flight = i;
  }
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
      addFlight(data.sfid, data.encoded.points, data.encoded.levels,
                data.num_levels, data.barogram_t, data.barogram_h, data.zoom_levels);

      map.events.triggerEvent("move");
      $.proxy(updateBarogram, { reset_y_axis: true })();
    }
  });
};


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
                        width: 1.5 });

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
  mouse_container.mousemove(function(e) {
    hidePlanePosition();

    var prop = linechart.getProperties();
    var kx_inv = 1 / prop.kx;
    var rel_x = e.clientX - mouse_container.offset().left;
    var x = prop.minx + (rel_x - prop.x - prop.gutter) * kx_inv;
    if (x < prop.minx || x > prop.maxx) return;

    // find the position indexes of all flight available.
    setIndexFromTime(x);

    // we'd like to have an flight within the current range as top_flight.
    if (flights[top_flight].index == -1) {
      // our current top flight is out of range. find first flight in range...
      for (top_flight in flights) if (flights[top_flight].index != -1) break;
    }

    // no flight found which is in range? return early, draw nothing.
    if (flights[top_flight].index == -1) return;

    // interpolate current height of top_flight
    var height = flights[top_flight].h[flights[top_flight].index] +
      (flights[top_flight].h[flights[top_flight].index+1] - flights[top_flight].h[flights[top_flight].index]) *
       flights[top_flight].dx;

    // calculate y-position of position marker for current top_flight and show marker
    var rel_y = prop.y - (height - prop.miny) * prop.ky + prop.height - prop.gutter;
    hoverColumn(flights[top_flight].index, rel_x, rel_y, top_flight);

    // draw plane icons on map
    for (fid in flights) {
      // do not show plane if out of range.
      if (flights[fid].index == -1) continue;

      showPlanePosition(flights[fid].index, flights[fid].dx, fid, (fid!=top_flight));
    }
  });

  // hide everything on mouse out
  mouse_container.mouseout(function(e) {
    hidePlanePosition();
    position && position.hide();
  });

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
    setTimeout(function() { linechart.zoomReset(reset_y_axis)}, 0);
  else
    // zoom linechart
    setTimeout(function() { linechart.zoomInto(total_first, total_last, reset_y_axis)}, 0);
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

    // hide everything
    hidePlanePosition();
    linechart.hoverColumn.position.hide();

    // if there's a aircraft within the bounding box, show the plane icon and draw
    // a position marker on the linechart.
    if (nearest !== null) {
      // we expect the currently hovered flight is the top flight.
      top_flight = nearest.fid;
      showPlanePosition(nearest.from, nearest.along, nearest.fid);

      var prop = linechart.getProperties();
      var x = flights[nearest.fid].t[nearest.from] + (flights[nearest.fid].t[nearest.from+1]-flights[nearest.fid].t[nearest.from])*nearest.along;

      if (x > prop.minx && x < prop.maxx) {
        // interpolate current height of nearest flight
        var height = flights[nearest.fid].h[nearest.from] +
          (flights[nearest.fid].h[nearest.to] - flights[nearest.fid].h[nearest.from]) *
           nearest.along;

        var rel_x = (x - prop.minx) * prop.kx + prop.x + prop.gutter;
        var rel_y = prop.y - (height - prop.miny) * prop.ky + prop.height - prop.gutter;
        linechart.hoverColumn(nearest.from, rel_x, rel_y, nearest.fid);
      }

      setIndexFromTime(x);
      for (fid in flights) {
        if (fid == nearest.fid || flights[fid].index == -1) continue;
        showPlanePosition(flights[fid].index, flights[fid].dx, fid, true);
      }
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

