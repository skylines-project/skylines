/**
 * Holds the OpenLayers map
 */
var map;


/**
 * Initialize the map and add airspace and flight path layers.
 *
 * @param {String} id The ID of the HTML element used for the map.
 * @param {String} tile_url The base URL of the SkyLines tile server.
 * @param {Object=} opt_options Optional options object.
 */
function initOpenLayers(id, tile_url, opt_options) {
  var options = opt_options || {};

  if (!options.base_layer) options.base_layer = 'OpenStreetMap';

  var interactions = ol.interaction.defaults({
    altShiftDragRotate: false,
    pinchRotate: false
  });

  map = new ol.Map({
    target: id,
    controls: ol.control.defaults().extend([
      new ol.control.ScaleLine(),
      new GraphicLayerSwitcher()
    ]),
    interactions: interactions,
    ol3Logo: false
  });

  map.getViewport().setAttribute('tabindex', '0');
  $(map.getViewport()).click(function() { $(this).focus() });


  map.getLayers().on('change:length', $.proxy(function() {
    // When the list of layers changes load the
    // last used base layer from the cookies
    setBaseLayer(this.options.base_layer || $.cookie('base_layer'));
    setOverlayLayers(this.options.overlay_layers || $.cookie('overlay_layers'));
  }, { options: options }));

  var osm_layer = new ol.layer.Tile({
    source: new ol.source.OSM(),
    name: 'OpenStreetMap',
    id: 'OpenStreetMap',
    base_layer: true,
    display_in_layer_switcher: true
  });

  // add layers according to their z-index...
  map.addLayer(osm_layer);
  addReliefLayer();

  addAirspaceLayers(tile_url);
  addMWPLayers(tile_url);

  map.getView().setCenter(
      ol.proj.transform([10, 50], 'EPSG:4326', 'EPSG:3857')
  );
  map.getView().setZoom(5);
}


function setBaseLayer(base_layer) {
  if (!base_layer)
    return;

  map.getLayers().forEach(function(layer) {
    if (layer.get('base_layer')) {
      layer.setVisible(layer.get('name') == base_layer);
    }
  });
}


function setOverlayLayers(overlay_layers) {
  if (!overlay_layers)
    return;

  overlay_layers = overlay_layers.split(';');

  // Cycle through the overlay layers to find a match
  map.getLayers().forEach(function(layer) {
    if (layer.get('base_layer') || !layer.get('display_in_layer_switcher'))
      return;

    if ($.inArray(layer.get('name'), overlay_layers) != -1)
      layer.setVisible(true);
    else
      layer.setVisible(false);
  });
}


/**
 * Add the custom Mountain Wave Project layer to the map

 * @param {String} tile_url The base URL of the mwp tile server.
 */
function addMWPLayers(tile_url) {
  if (!tile_url) tile_url = '';

  var mwp_layer = new ol.layer.Tile({
    source: new ol.source.XYZ({
      attributions: [
        new ol.Attribution({
          html: 'Mountain Wave Data &copy; ' +
              '<a href="http://www.mountain-wave-project.com/">' +
              'Mountain Wave Project' +
              '</a>.'
        })
      ],
      url: tile_url + '/tiles/1.0.0/mwp/{z}/{x}/{y}.png'
    }),
    name: 'Mountain Wave Project',
    id: 'MountainWaveProject',
    base_layer: false,
    display_in_layer_switcher: true
  });

  map.addLayer(mwp_layer);
}


/**
 * Add the custom airspace layers to the map

 * @param {String} tile_url The base URL of the airspace tile server.
 */
function addAirspaceLayers(tile_url) {
  if (!tile_url) tile_url = '';

  var airspace_layer = new ol.layer.Tile({
    source: new ol.source.XYZ({
      url: tile_url + '/tiles/1.0.0/airspace+airports/{z}/{x}/{y}.png'
    }),
    name: 'Airspace',
    id: 'Airspace',
    base_layer: false,
    display_in_layer_switcher: true
  });

  map.addLayer(airspace_layer);
}


/**
 * Add the maps-for-free shaded relief layer to the map
 */
function addReliefLayer() {
  var url =
      'http://maps-for-free.com/layer/relief/z{z}/row{y}/{z}_{x}-{y}.jpg';

  var relief_layer = new ol.layer.Tile({
    source: new ol.source.XYZ({
      attributions: [
        new ol.Attribution({
          html: 'SRTM relief maps from <a target="_blank" ' +
              'href="http://maps-for-free.com/">maps-for-free.com</a>'
        })
      ],
      url: url
    }),
    name: 'Shaded Relief',
    id: 'ShadedRelief',
    base_layer: true,
    display_in_layer_switcher: true
  });

  map.addLayer(relief_layer);
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
    base_layer: true,
    display_in_layer_switcher: true
  });

  // Bing's AerialWithLabels imagerySet
  var hybrid = new OpenLayers.Layer.Bing({
    key: api_key,
    type: 'AerialWithLabels',
    name: 'Bing Satellite',
    base_layer: true,
    display_in_layer_switcher: true
  });

  map.addLayers([road, hybrid]);
}

/*
 * Add the InfoBox handler to the map.
 *
 * @param {Object} settings Set flight_info or location_info to true to enable
 */
function initInfoBox(settings) {
  // add click handler for nearest flight search
  var map_click_handler = slMapClickHandler(map, settings);
  map.on('click', map_click_handler.trigger);
}
