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
      'default': new OpenLayers.Style({
        strokeColor: "${color}",
        strokeWidth: 2,
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
      })
    })
  });
     
  map.addLayer(flightPathLayer);
//  map.events.register("moveend", flightPathLayer, flightPathLayer.redraw);

  map.setCenter(new OpenLayers.LonLat(30, 0).
    transform(new OpenLayers.Projection("EPSG:4326"),map.getProjectionObject() ),
    9);

  var initRedrawLayer = function(layer) {
    if (this.timer) return;
    this.timer = window.setTimeout(function() { this.timer = null; layer.redraw(); }.bind(this), 200);
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

// add leading zeros to a number
function pad(num, size) {
  var s = "000000000" + num;
  return s.substr(s.length-size);
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
    opacity: .7,
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

  linechart.hoverColumn(function() {
    hoverLine.attr({ path:
      "M " + this.x.toString() + " " + this.attrs.height + " " +
      "l 0 " + (-(this.attrs.height - this.y) + 6).toString() +
      "M " + this.x.toString() + " 0 " +
      "l 0 " + (this.y - 6).toString()
    });
    var vario = null;
    if (this.next && this.next.values) {
      vario = (this.next.values[0] - this.values[0]) / (this.next.axis - this.axis);
    }

    text.attr({
      x: this.x,
      y: this.attrs.height - 20,
      text: Math.round(this.values[0]) + " m" +
            ((vario !== null)?"\n" + (Math.round(vario*10)/10) + " m/s":"")
    });

    hoverCircle.attr({
      cx: this.x,
      cy: this.y,
    });

    var textBBox = text.getBBox();
    textRect.attr({
      x: textBBox.x - 2,
      y: textBBox.y - 2,
      width: textBBox.width + 4,
      height: textBBox.height + 4
    });

    position.show();

    this.index = getNearestNumber(barogram_t, this.axis);
    showPlanePosition(this.index);
  }, function() {
    hidePlanePosition(this.index);
    position && position.hide();
  });

  return barogram;
}

function showPlanePosition(id) {
  var rotation = 0;
  if (lonlat[id+1] != 'undefined') {
    rotation = Math.atan2(lonlat[id+1].lon-lonlat[id].lon, lonlat[id+1].lat-lonlat[id].lat) * 180/Math.PI;
  } else if (lonlat[id-1] != 'undefined') {
    rotation = Math.atan2(lonlat[id].lon-lonlat[id-1].lon, lonlat[id].lat-lonlat[id-1].lat) * 180/Math.PI;
  }
  plane.attributes.rotation = rotation;
  plane.geometry = new OpenLayers.Geometry.Point(lonlat[id].lon, lonlat[id].lat).
    transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
  map.getLayersByName("Flight")[0].drawFeature(plane);
}

function hidePlanePosition(id) {
  map.getLayersByName("Flight")[0].removeFeatures(plane);
}

