/* globals ol, isCanvasSupported, GraphicLayerSwitcher */

import Ember from 'ember';

export default Ember.Component.extend(Ember.Evented, {
  attributeBindings: ['style'],

  width: '100%',
  height: '100%',
  bingAPIKey: null,
  mapboxAPIKey: null,
  mapTileURL: null,
  baseLayer: null,

  style: Ember.computed('width', 'height', function() {
    let { width, height } = this.getProperties('width', 'height');
    return `width: ${width}; height: ${height};`;
  }),

  noCanvas: Ember.computed(function() {
    return !isCanvasSupported();
  }),

  init() {
    this._super(...arguments);

    window.flightMap = this;
  },

  didInsertElement() {
    if (this.get('noCanvas')) {
      return;
    }

    let interactions = ol.interaction.defaults({
      altShiftDragRotate: false,
      pinchRotate: false
    });

    let map = new ol.Map({
      target: this.elementId,
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
    this.set('map', map);

    map.getViewport().setAttribute('tabindex', '0');
    Ember.$(map.getViewport()).click(function() {
      Ember.$(this).focus();
    });

    map.getLayers().on('change:length', () => {
      // When the list of layers changes load the
      // last used base layer from the cookies
      this.setBaseLayer(this.get('baseLayer') || Ember.$.cookie('base_layer'));
      this.setOverlayLayers(this.get('overlayLayers') || Ember.$.cookie('overlay_layers'));
    });

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

    this.addReliefLayer();
    this.addAirspaceLayers();
    this.addMWPLayers();
    this.addBingLayers();
    this.addMapboxLayer();
  },

  setBaseLayer(base_layer) {
    if (!base_layer) {
      return;
    }

    var fallback = false;
    var map = this.get('map');

    map.getLayers().forEach(layer => {
      if (layer.get('base_layer')) {
        layer.setVisible(layer.get('name') === base_layer);
        fallback = fallback || layer.get('name') === base_layer;
      }
    });

    if (!fallback) {
      map.getLayers().getArray().filter(function(e) {
        return e.get('name') === 'OpenStreetMap';
      })[0].setVisible(true);
    }
  },

  setOverlayLayers(overlay_layers) {
    if (!overlay_layers) {
      return;
    }

    overlay_layers = overlay_layers.split(';');

    // Cycle through the overlay layers to find a match
    this.get('map').getLayers().forEach(layer => {
      if (layer.get('base_layer') || !layer.get('display_in_layer_switcher')) {
        return;
      }

      layer.setVisible(Ember.$.inArray(layer.get('name'), overlay_layers) !== -1);
    });
  },

  addMWPLayers() {
    let tile_url = this.getWithDefault('mapTileURL', '');

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

    this.get('map').addLayer(mwp_layer);
  },

  addAirspaceLayers() {
    let tile_url = this.getWithDefault('mapTileURL', '');

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

    this.get('map').addLayer(airspace_layer);
  },

  addReliefLayer() {
    var url = 'http://maps-for-free.com/layer/relief/z{z}/row{y}/{z}_{x}-{y}.jpg';

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

    this.get('map').addLayer(relief_layer);
  },

  addMapboxLayer() {
    let tile_url = this.get('mapboxAPIKey');
    if (!tile_url || tile_url == 'null') {
      return;
    }

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

    this.get('map').addLayer(mapbox_layer);
  },

  addBingLayers() {
    let api_key = this.get('bingAPIKey');
    if (!api_key || api_key == 'null') {
      return;
    }

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

    let map = this.get('map');
    map.addLayer(road);
    map.addLayer(hybrid);
  },
});
