/**
 * Holds the OpenLayers map
 */
var map;

/**
 * Initialize the map and add airspace and flight path layers.
 *
 * @param {String} id The ID of the HTML element used for the map.
 * @param {String} airspace_tile_url The base URL of the airspace tile server.
 */
function initOpenLayers(id, airspace_tile_url) {
  OpenLayers.ImgPath = '/images/OpenLayers/';

  map = new OpenLayers.Map(id, {
    projection: 'EPSG:900913',
    controls: [],
    theme: null
  });

  map.div.setAttribute('tabindex', '0');
  $(map.div).click(function() { $(this).focus() });

  map.addControl(new OpenLayers.Control.Zoom());
  map.addControl(new OpenLayers.Control.Navigation({documentDrag: true}));
  map.addControl(new OpenLayers.Control.KeyboardDefaults({
    observeElement: map.div
  }));
  map.addControl(new OpenLayers.Control.Attribution());
  map.addControl(new OpenLayers.Control.ScaleLine({geodesic: true}));

  var osmLayer = new OpenLayers.Layer.OSM('OpenStreetMap');
  osmLayer.addOptions({
    transitionEffect: 'resize',
    numZoomLevels: 18
  });

  map.addLayer(osmLayer);

  addAirspaceLayers(airspace_tile_url);
  addEmptyLayer();

  map.setCenter(new OpenLayers.LonLat(30, 0).
    transform(new OpenLayers.Projection('EPSG:4326'),
              map.getProjectionObject()),
    9);

  map.addControl(new GraphicLayerSwitcher());

  map.events.register('changebaselayer', null, function(data) {
    // Save the selected base layer in a cookie
    $.cookie('base_layer', data.layer.name, { path: '/', expires: 365 });
  });

  map.events.register('addlayer', null, function() {
    // When the list of layers changes load the
    // last used base layer from the cookies
    loadBaseLayerFromCookie();
  });
}

function loadBaseLayerFromCookie() {
  var base_layer = $.cookie('base_layer');
  if (base_layer == null)
    return;

  // Cycle through the base layers to find a match
  base_layer = map.getLayersByName(base_layer)[0];
  if (base_layer)
    // If the base layer names are matching set this layer as new base layer
    map.setBaseLayer(base_layer);
}

/**
 * Add the custom airspace layers to the map

 * @param {String} airspace_tile_url The base URL of the airspace tile server.
 */
function addAirspaceLayers(airspace_tile_url) {
  if (!airspace_tile_url) airspace_tile_url = '';

  var airspace = new OpenLayers.Layer.XYZ('Airspace',
    airspace_tile_url + '/mapproxy/tiles/1.0.0/airspace/${z}/${x}/${y}.png', {
    isBaseLayer: false,
    transparent: true,
    'visibility': true,
    'displayInLayerSwitcher': true
  });
  map.addLayer(airspace);

  map.events.register('changebaselayer', null, function(data) {
    if (data.layer.hideAirspaceOverlay)
      airspace.setVisibility(false);
  });
}

/**
 * Add the maps-for-free shaded relief layer to the map
 */
function addReliefLayer() {
  var url =
      'http://maps-for-free.com/layer/relief/z${z}/row${y}/${z}_${x}-${y}.jpg';
  var relief = new OpenLayers.Layer.XYZ('Shaded Relief', url, {
    sphericalMercator: true,
    numZoomLevels: 12,
    attribution: 'SRTM relief maps from <a target="_blank" ' +
                  'href="http://maps-for-free.com/">maps-for-free.com</a>'
  });

  map.addLayer(relief);
}

/**
 * Add the Bing layers to the map
 *
 * @param {String} api_key The API key supplied by Bing.
 */
function addBingLayers(api_key) {
  if (api_key == 'null')
    return;

  // Bing's Road imagerySet
  var road = new OpenLayers.Layer.Bing({
      key: api_key,
      type: 'Road',
      name: 'Bing Road',
      hideAirspaceOverlay: true
  });

  // Bing's AerialWithLabels imagerySet
  var hybrid = new OpenLayers.Layer.Bing({
      key: api_key,
      type: 'AerialWithLabels',
      name: 'Bing Satellite',
      hideAirspaceOverlay: true
  });

  map.addLayers([road, hybrid]);
}

/**
 * Callback when Google Maps API has been loaded.
 * Add the google physical layer to the map
 */
function addGoogleLayer() {
  // add google maps if google script loaded
  if (window.google) {
    var google_physical_layer = new OpenLayers.Layer.Google(
      'Google Physical',
      {type: google.maps.MapTypeId.TERRAIN}
    );
    map.addLayer(google_physical_layer);

    var google_satellite_layer = new OpenLayers.Layer.Google(
      'Google Satellite',
      {type: google.maps.MapTypeId.HYBRID}
    );
    map.addLayer(google_satellite_layer);
  }
}

/**
 * Add a empty layer to the map
 */
function addEmptyLayer() {
  var empty_layer = new OpenLayers.Layer('Empty', {
    isBaseLayer: true
  });

  map.addLayer(empty_layer);
}

