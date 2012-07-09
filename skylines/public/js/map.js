/**
 * map
 *
 * Holds the OpenLayers map
 */
var map;

/**
 * Function initOpenLayers
 *
 * Initialize the map and add airspace and flight path layers.
 */
function initOpenLayers(id) {
  OpenLayers.ImgPath = "/images/OpenLayers/"

  map = new OpenLayers.Map(id, {
    projection: "EPSG:900913",
    controls: [],
    theme: null
  });

  map.addControl(new OpenLayers.Control.Zoom());
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
    "/mapproxy/tiles/1.0.0/airspace/${z}/${x}/${y}.png?origin=nw", {
    isBaseLayer: false,
    transparent: true,
    'visibility': true,
    'displayInLayerSwitcher': true
  });
  map.addLayer(airspace);

  map.setCenter(new OpenLayers.LonLat(30, 0).
    transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject()),
    9);

  map.addControl(new SimpleLayerSwitcher());
};

/**
 * Function: addBingLayers
 *
 * Add the Bing layers to the map
 */
function addBingLayers(api_key) {
  if (api_key == 'null')
    return;

  // Bing's Road imagerySet
  var road = new OpenLayers.Layer.Bing({
      key: api_key,
      type: "Road"
  });

  // Bing's AerialWithLabels imagerySet
  var hybrid = new OpenLayers.Layer.Bing({
      key: api_key,
      type: "AerialWithLabels",
      name: "Bing Satellite"
  });

  map.addLayers([road, hybrid]);

  // disable airspace layer when bing layers are shown
  // seems to be due to off-by-one bug of zoomLevel, see https://github.com/openlayers/openlayers/issues/418
  // should be reverted if the OL bug is fixed.
  var airspace = map.getLayersByName('Airspace')[0];
  map.events.register('changebaselayer', this, function() {
    if (road.getVisibility() || hybrid.getVisibility()) {
      airspace.setVisibility(false);
    } else {
      airspace.setVisibility(true);
    }
  });
}

/**
 * Function: addGoogleLayer
 *
 * Callback when Google Maps API has been loaded.
 * Add the google physical layer to the map
 */
function addGoogleLayer() {
  // add google maps if google script loaded
  if (window.google) {
    var google_physical_layer = new OpenLayers.Layer.Google(
      "Google Physical",
      {type: google.maps.MapTypeId.TERRAIN}
    );
    map.addLayer(google_physical_layer);

    var google_satellite_layer = new OpenLayers.Layer.Google(
      "Google Satellite",
      {type: google.maps.MapTypeId.HYBRID}
    );
    map.addLayer(google_satellite_layer);
  }
}
