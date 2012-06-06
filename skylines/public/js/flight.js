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
        externalGraphic: "/images/OpenLayers/marker.png",
        // Makes sure the background graphic is placed correctly relative
        // to the external graphic.
        graphicXOffset: -(21/2),
        graphicYOffset: -25,
        graphicWidth: 21,
        graphicHeight: 25,
        // Set the z-indexes of both graphics to make sure the background
        // graphics stay in the background (shadows on top of markers looks
        // odd; let's not do that).
        graphicZIndex: 2000
      })
    })
  });
     
  map.addLayer(flightPathLayer);
  map.events.register("moveend", flightPathLayer, flightPathLayer.redraw);

  map.setCenter(new OpenLayers.LonLat(30, 0).
    transform(new OpenLayers.Projection("EPSG:4326"),map.getProjectionObject() ),
    9);

  return map;
};
