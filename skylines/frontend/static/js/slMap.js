


/**
 * The SkyLines map instance
 * @constructor
 * @export
 * @param {String} _id The ID of the HTML element used for the map.
 * @param {String} _tile_url The base URL of the SkyLines tile server.
 * @param {Object=} opt_options Optional options object.
 */
slMap = function(_id, _tile_url, opt_options) {
  var sl_map = this;

  var options = opt_options || {};

  var id = _id;
  var tile_url = _tile_url;

  /**
   * Holds the OpenLayers map
   */
  var map;


  /**
   * Initialize the map and add airspace and flight path layers.
   */
  sl_map.init = function() {
    if (!options['base_layer'] && !$.cookie('base_layer'))
      options['base_layer'] = 'OpenStreetMap';

    var interactions = ol.interaction.defaults({
      altShiftDragRotate: false,
      pinchRotate: false
    });

    map = new ol.Map({
      target: id,
      view: new ol.View({
        center: ol.proj.transform([10, 50], 'EPSG:4326', 'EPSG:3857'),
        maxZoom: 17,
        zoom: 5
      }),
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
      sl_map.setBaseLayer(this.options['base_layer'] || $.cookie('base_layer'));
      sl_map.setOverlayLayers(this.options['overlay_layers'] ||
                              $.cookie('overlay_layers'));
    }, { options: options }));

    var osm_layer = new ol.layer.Tile({
      source: new ol.source.OSM(),
      zIndex: 1
    });

    osm_layer.setProperties({
      'name': 'OpenStreetMap',
      'id': 'OpenStreetMap',
      'base_layer': true,
      'display_in_layer_switcher': true
    });

    map.addLayer(osm_layer);
    sl_map.addReliefLayer();

    sl_map.addAirspaceLayers(tile_url);
    sl_map.addMWPLayers(tile_url);
  };


  sl_map.setBaseLayer = function(base_layer) {
    if (!base_layer)
      return;

    var fallback = false;

    map.getLayers().forEach(function(layer) {
      if (layer.get('base_layer')) {
        layer.setVisible(layer.get('name') == base_layer);
        fallback |= layer.get('name') == base_layer;
      }
    });

    if (!fallback)
      map.getLayers().getArray().filter(function(e) {
        return e.get('name') == 'OpenStreetMap';
      })[0].setVisible(true);
  };


  sl_map.setOverlayLayers = function(overlay_layers) {
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
  };


  /**
   * Add the custom Mountain Wave Project layer to the map
   * @param {String} tile_url The base URL of the mwp tile server.
   */
  sl_map.addMWPLayers = function(tile_url) {
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
      zIndex: 11
    });

    mwp_layer.setProperties({
      'name': 'Mountain Wave Project',
      'id': 'MountainWaveProject',
      'base_layer': false,
      'display_in_layer_switcher': true
    });

    map.addLayer(mwp_layer);
  };


  /**
   * Add the custom airspace layers to the map
   * @param {String} tile_url The base URL of the airspace tile server.
   */
  sl_map.addAirspaceLayers = function(tile_url) {
    if (!tile_url) tile_url = '';

    var airspace_layer = new ol.layer.Tile({
      source: new ol.source.XYZ({
        url: tile_url + '/tiles/1.0.0/airspace+airports/{z}/{x}/{y}.png'
      }),
      zIndex: 10
    });

    airspace_layer.setProperties({
      'name': 'Airspace',
      'id': 'Airspace',
      'base_layer': false,
      'display_in_layer_switcher': true
    });

    map.addLayer(airspace_layer);
  };


  /**
   * Add the maps-for-free shaded relief layer to the map
   */
  sl_map.addReliefLayer = function() {
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
      zIndex: 2
    });

    relief_layer.setProperties({
      'name': 'Shaded Relief',
      'id': 'ShadedRelief',
      'base_layer': true,
      'display_in_layer_switcher': true
    });

    map.addLayer(relief_layer);
  };

  sl_map.init();

  sl_map.map = map;
  return sl_map;
};


/**
 * Add the Mapbox layer to the map
 *
 * @export
 * @param {String} tile_url The tile url supplied by Mapbox
 */
slMap.prototype.addMapboxLayer = function(tile_url) {
  if (tile_url == 'null') return;

  var mapbox_layer = new ol.layer.Tile({
    source: new ol.source.XYZ({
      attributions: [
        new ol.Attribution({
          html: '<a href="https://www.mapbox.com/about/maps/"' +
              ' target="_blank">' +
              '&copy; Mapbox &copy; OpenStreetMap</a> <a' +
              ' class="mapbox-improve-map"' +
              ' href="https://www.mapbox.com/map-feedback/"' +
              ' target="_blank">Improve this map</a>'
        })
      ],
      url: tile_url
    }),
    zIndex: 5
  });

  mapbox_layer.setProperties({
    'name': 'Terrain',
    'id': 'Terrain',
    'base_layer': true,
    'display_in_layer_switcher': true
  });

  this.map.addLayer(mapbox_layer);
};


/**
 * Add the Bing layers to the map
 *
 * @export
 * @param {String} api_key The API key supplied by Bing.
 */
slMap.prototype.addBingLayers = function(api_key) {
  if (api_key == 'null')
    return;

  // Bing's Road imagerySet
  var road = new ol.layer.Tile({
    source: new ol.source.BingMaps({
      key: api_key,
      imagerySet: 'Road'
    }),
    zIndex: 3
  });

  road.setProperties({
    'name': 'Bing Road',
    'id': 'BingRoad',
    'base_layer': true,
    'display_in_layer_switcher': true
  });

  // Bing's AerialWithLabels imagerySet
  var hybrid = new ol.layer.Tile({
    source: new ol.source.BingMaps({
      key: api_key,
      imagerySet: 'AerialWithLabels'
    }),
    zIndex: 4
  });

  hybrid.setProperties({
    'name': 'Bing Satellite',
    'id': 'BingSatellite',
    'base_layer': true,
    'display_in_layer_switcher': true
  });

  this.map.addLayer(road);
  this.map.addLayer(hybrid);
};


/**
 * Return the map object.
 *
 * @export
 * @return {ol.Map} map Object
 */
slMap.prototype.getMap = function() {
  return this.map;
};
