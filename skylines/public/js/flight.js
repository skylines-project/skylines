function initOpenLayers() {
  OpenLayers.ImgPath = "/images/OpenLayers/"

  var map = new OpenLayers.Map("map_canvas", {
    projection: "EPSG:900913",
    controls: [],
    theme: null
  });

  map.addControl(new OpenLayers.Control.PanZoomBar());
  map.addControl(new OpenLayers.Control.Navigation());
  map.addControl(new OpenLayers.Control.KeyboardDefaults());
  map.addControl(new OpenLayers.Control.Attribution());
  map.addControl(new OpenLayers.Control.ScaleLine({geodesic: true}));

  var osmLayer = new OpenLayers.Layer.OSM("OpenStreetMap");
  osmLayer.addOptions({
    transitionEffect: "resize",
    numZoomLevels: 18
  });

  map.addLayer(osmLayer);

  var airspace = new OpenLayers.Layer.XYZ("Airspace",
    "http://www.prosoar.de/airspace/${z}/${x}/${y}.png", {
    isBaseLayer: false,
    transparent: true,
    'visibility': true,
    'displayInLayerSwitcher': true
  });
  map.addLayer(airspace);

  var flightPathLayer = new OpenLayers.Layer.Vector("Flight", {
    styleMap: new OpenLayers.StyleMap({
      'default': {
        strokeColor: "${color}",
        strokeWidth: 2
      },
      'plane': {
        // Set the external graphic and background graphic images.
        externalGraphic: "/images/glider_symbol.png",
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
      }
    })
  });
     
  map.addLayer(flightPathLayer);
//  map.events.register("moveend", flightPathLayer, flightPathLayer.redraw);

  map.setCenter(new OpenLayers.LonLat(30, 0).
    transform(new OpenLayers.Projection("EPSG:4326"),map.getProjectionObject() ),
    9);

  var initRedrawLayer = function(layer) {
    if (this.timer) return;
    this.timer = window.setTimeout(function() { this.timer = null; layer.redraw(); }, 200);
  };
  map.events.register("move", this, function() { initRedrawLayer(flightPathLayer); });

  return map;
};

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

function formatSecondsAsTime(seconds) {
  seconds %= 86400;
  var h = Math.floor(seconds/3600);
  var m = Math.floor((seconds%3600)/60);
  var s = Math.floor(seconds%3600%60);

  return pad(h,2) + ":" + pad(m,2) + ":" + pad(s,2); // Format the result into time strings
}

function render_barogram(element) {
  var barogram = Raphael("barogram", "100%", "100%");

  var linechart = barogram.linechart(30, 0,
                      element.innerWidth() - 50, element.innerHeight() - 10,
                      barogram_t,
                      [barogram_h],
                      { axis: "0 0 1 1",
                        axisxstep: 8,
                        axisxfunc: formatSecondsAsTime });

  var position = barogram.set().hide();

  var hoverLine = barogram.path().attr({
    stroke: '#c44',
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
    stroke: '#c44',
    'stroke-width': 2,
    r: 6
  }).hide();

  position.push(hoverLine);
  position.push(hoverCircle);
  position.push(textRect.insertAfter(hoverCircle));
  position.push(text.insertAfter(textRect));

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

  mouse_container.mousemove(function(e) {
    hidePlanePosition();
    var prop = linechart.getProperties();
    var kx_inv = 1 / prop.kx;
    var rel_x = e.clientX - mouse_container.offset().left;
    var x = prop.minx + (rel_x - prop.x - prop.gutter) * kx_inv;
    if (x < prop.minx || x > prop.maxx) return;

    var baro_index = getNearestNumber(barogram_t, x);
    var rel_y = prop.y - (barogram_h[baro_index] - prop.miny) * prop.ky + prop.height - prop.gutter;

    hoverColumn(baro_index, rel_x, rel_y);

    if (x < barogram_t[baro_index]) {
      var dx = (x - barogram_t[baro_index-1])/(barogram_t[baro_index] - barogram_t[baro_index-1]);
      showPlanePosition(baro_index - 1, dx);
    } else {
      var dx = (x - barogram_t[baro_index])/(barogram_t[baro_index+1] - barogram_t[baro_index]);
      showPlanePosition(baro_index, dx);
    }
  });

  mouse_container.mouseout(function(e) {
    hidePlanePosition();
    position && position.hide();
  });

  hoverColumn = function(index, x, y) {
    position.toFront();
    var attrs = linechart.getProperties();

    hoverLine.attr({ path:
      "M " + x.toString() + " " + attrs.height + " " +
      "l 0 " + (-(attrs.height - y) + 6).toString() +
      "M " + x.toString() + " 0 " +
      "l 0 " + (y - 6).toString()
    });

    var vario = null;
    if (barogram_t[index+1] != undefined) {
      vario = (barogram_h[index+1] - barogram_h[index]) / (barogram_t[index+1] - barogram_t[index]);
    }

    var speed = null;
    if (barogram_t[index+1] != undefined) {
      speed = OpenLayers.Util.distVincenty(lonlat[index+1], lonlat[index]);
      speed *= 1000;
      speed /= (barogram_t[index+1] - barogram_t[index]);
    }

    text.attr({
      x: x,
      y: attrs.height - 20,
      text: Math.round(barogram_h[index]) + " m" +
            ((vario !== null)?"\n" + (Math.round(vario*10)/10) + " m/s":"") +
            ((speed !== null)?"\n" + (Math.round(speed*3.6*10)/10) + " km/h":"") +
            "\n" + formatSecondsAsTime(barogram_t[index])
    });

    hoverCircle.attr({
      cx: x,
      cy: y
    });

    var textBBox = text.getBBox();
    textRect.attr({
      x: textBBox.x - 2,
      y: textBBox.y - 2,
      width: textBBox.width + 4,
      height: textBBox.height + 4
    });

    position.show();
  };

  return linechart;
}

function showPlanePosition(id, dx) {
  var rotation = 0;
  if (lonlat[id+1] != 'undefined') {
    rotation = Math.atan2(lonlat[id+1].lon-lonlat[id].lon, lonlat[id+1].lat-lonlat[id].lat) * 180/Math.PI;
  } else if (lonlat[id-1] != 'undefined') {
    rotation = Math.atan2(lonlat[id].lon-lonlat[id-1].lon, lonlat[id].lat-lonlat[id-1].lat) * 180/Math.PI;
  }

  var lon = lonlat[id].lon + (lonlat[id+1].lon - lonlat[id].lon)*dx;
  var lat = lonlat[id].lat + (lonlat[id+1].lat - lonlat[id].lat)*dx;

  plane.attributes.rotation = rotation;
  plane.geometry = new OpenLayers.Geometry.Point(lon, lat).
    transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
  map.getLayersByName("Flight")[0].drawFeature(plane);
}

function hidePlanePosition() {
  map.getLayersByName("Flight")[0].removeFeatures(plane);
}

function scaleBarogram(linechart, flight, element) {

  var updateBarogram = function(e) {
    var largest_partition = null;
    var delta_t = 0;
    var first = 0;
    var last = barogram_t.length - 1;

    // only show longest single part of trace in barogram
    for (part_geo in flight.partitionedGeometries) {
      var components = flight.partitionedGeometries[part_geo].components;
      var temp = barogram_t[components[components.length-1].originalIndex] -
        barogram_t[components[0].originalIndex];

      if (temp > delta_t) {
        delta_t = temp;
        largest_partition = part_geo;
        first = components[0].originalIndex;
        last = components[components.length-1].originalIndex;
      }
    }

/*
    // show barogram of all trace parts visible
    var length = flight.partitionedGeometries.length;
    var comp_length = flight.partitionedGeometries[length-1].components.length;
    first = flight.partitionedGeometries[0].components[0].originalIndex;
    last = flight.partitionedGeometries[length-1].components[comp_length-1].originalIndex;
*/
    setTimeout(function() { linechart.zoomInto(first, last)}, 0);
  };

  map.events.register("moveend", this, updateBarogram);
}

function hoverMap(map, flight) {
  var running = false;
  map.events.register("mousemove", this, function(e) {
    // call this function only every 25ms
    if (running) return;
    running = true;
    setTimeout(function() { running = false; }, 25);

    var pixel = e.xy.clone();
    var hoverTolerance = 15;
    var llPx = pixel.add(-hoverTolerance/2, hoverTolerance/2);
    var urPx = pixel.add(hoverTolerance/2, -hoverTolerance/2);
    var ll = map.getLonLatFromPixel(llPx);
    var ur = map.getLonLatFromPixel(urPx);
    var loc = map.getLonLatFromPixel(pixel);

    var nearest = searchForPlane(new OpenLayers.Bounds(ll.lon, ll.lat, ur.lon, ur.lat), loc);

    hidePlanePosition();
    if (nearest !== null) showPlanePosition(nearest.from, nearest.along);
  });

  function searchForPlane(within, loc) {
    var possible_solutions = [];

    for (part_geo in flight.partitionedGeometries) {
      for (var i = 1, len = flight.partitionedGeometries[part_geo].components.length; i < len; i++) {
        var vector = new OpenLayers.Bounds();
        vector.extend(flight.partitionedGeometries[part_geo].components[i-1]);
        vector.extend(flight.partitionedGeometries[part_geo].components[i]);

        if (within.intersectsBounds(vector))
          possible_solutions.push({
            from: flight.partitionedGeometries[part_geo].components[i-1].originalIndex,
            to: flight.partitionedGeometries[part_geo].components[i].originalIndex
          });
      }
    }

    if (possible_solutions.length == 0) return null;

    var nearest, distance = 99999999999;
    for (i in possible_solutions) {
      for (var j = possible_solutions[i].from + 1; j <= possible_solutions[i].to; j++) {
        var distToSegment = distanceToSegmentSquared({x: loc.lon, y: loc.lat},
          { x1: flight.components[j-1].x, y1: flight.components[j-1].y,
            x2: flight.components[j].x, y2: flight.components[j].y });


        if (distToSegment.distance < distance) {
          distance = distToSegment.distance;
          nearest = { from: j-1, to: j, along: distToSegment.along };
        }
      }
    }

    return nearest;
  };

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

