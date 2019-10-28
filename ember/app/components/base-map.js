import Component from '@ember/component';
import { observer } from '@ember/object';
import { once } from '@ember/runloop';
import { inject as service } from '@ember/service';

import $ from 'jquery';
import ol from 'openlayers';

import config from '../config/environment';

export default Component.extend({
  tagName: '',

  mapSettings: service(),

  mapSettingsObserver: observer('mapSettings.baseLayer', 'mapSettings.overlayLayers.[]', function() {
    once(this, 'updateLayerVisibilities');
  }),

  init() {
    this._super(...arguments);

    window.flightMap = this;

    let interactions = ol.interaction.defaults({
      altShiftDragRotate: false,
      pinchRotate: false,
    });

    let map = new ol.Map({
      view: new ol.View({
        center: ol.proj.transform([10, 50], 'EPSG:4326', 'EPSG:3857'),
        maxZoom: 17,
        zoom: 5,
      }),
      controls: ol.control.defaults().extend([new ol.control.ScaleLine()]),
      interactions,
      ol3Logo: false,
    });
    this.set('map', map);

    map.getViewport().setAttribute('tabindex', '0');
    $(map.getViewport()).click(function() {
      $(this).focus();
    });

    let osm_layer = new ol.layer.Tile({
      source: new ol.source.OSM(),
      zIndex: 1,
    });

    osm_layer.setProperties({
      name: 'OpenStreetMap',
      id: 'OpenStreetMap',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    map.addLayer(osm_layer);

    this.addReliefLayer();
    this.addAirspaceLayers();
    this.addMWPLayers();
    this.addBingLayers();
    this.addMapboxLayer();
    this.addEmptyLayer();

    this.updateLayerVisibilities();
  },

  updateLayerVisibilities() {
    let mapSettings = this.mapSettings;
    let baseLayerNames = mapSettings.get('baseLayer');
    let overlayLayerNames = mapSettings.get('overlayLayers');

    let layers = this.map
      .getLayers()
      .getArray()
      .filter(layer => layer.get('display_in_layer_switcher'));

    let baseLayers = layers.filter(layer => layer.get('base_layer'));
    baseLayers.forEach(layer => {
      layer.setVisible(layer.get('name') === baseLayerNames);
    });

    if (!baseLayers.find(layer => layer.get('name') === baseLayerNames)) {
      baseLayers.find(layer => layer.get('name') === 'OpenStreetMap').setVisible(true);
    }

    let overlayLayers = layers.filter(layer => !layer.get('base_layer'));
    overlayLayers.forEach(layer => {
      layer.setVisible(overlayLayerNames.includes(layer.get('name')));
    });
  },

  addMWPLayers() {
    let mwp_layer = new ol.layer.Tile({
      source: new ol.source.XYZ({
        attributions: [
          new ol.Attribution({
            html:
              'Mountain Wave Data &copy; ' +
              '<a href="http://www.mountain-wave-project.com/">' +
              'Mountain Wave Project' +
              '</a>.',
          }),
        ],
        url: `${config.SKYLINES_TILE_BASEURL || ''}/tiles/1.0.0/mwp/EPSG3857/{z}/{x}/{y}.png`,
      }),
      zIndex: 11,
    });

    mwp_layer.setProperties({
      name: 'Mountain Wave Project',
      id: 'MountainWaveProject',
      base_layer: false,
      display_in_layer_switcher: true,
    });

    this.map.addLayer(mwp_layer);
  },

  addAirspaceLayers() {
    let airspace_layer = new ol.layer.Tile({
      source: new ol.source.XYZ({
        url: `${config.SKYLINES_TILE_BASEURL || ''}/tiles/1.0.0/airspace+airports/EPSG3857/{z}/{x}/{y}.png`,
      }),
      zIndex: 10,
    });

    airspace_layer.setProperties({
      name: 'Airspace',
      id: 'Airspace',
      base_layer: false,
      display_in_layer_switcher: true,
    });

    this.map.addLayer(airspace_layer);
  },

  addReliefLayer() {
    let url = 'http://maps-for-free.com/layer/relief/z{z}/row{y}/{z}_{x}-{y}.jpg';

    let relief_layer = new ol.layer.Tile({
      source: new ol.source.XYZ({
        attributions: [
          new ol.Attribution({
            html:
              'SRTM relief maps from <a target="_blank" rel="noopener" ' +
              'href="http://maps-for-free.com/">maps-for-free.com</a>',
          }),
        ],
        url,
      }),
      zIndex: 2,
    });

    relief_layer.setProperties({
      name: 'Shaded Relief',
      id: 'ShadedRelief',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    this.map.addLayer(relief_layer);
  },

  addMapboxLayer() {
    let tile_url = config.MAPBOX_TILE_URL;
    if (!tile_url) {
      return;
    }

    let mapbox_layer = new ol.layer.Tile({
      source: new ol.source.XYZ({
        attributions: [
          new ol.Attribution({
            html:
              '<a href="https://www.mapbox.com/about/maps/"' +
              ' target="_blank" rel="noopener">' +
              '&copy; Mapbox &copy; OpenStreetMap</a> <a' +
              ' class="mapbox-improve-map"' +
              ' href="https://www.mapbox.com/map-feedback/"' +
              ' target="_blank" rel="noopener">Improve this map</a>',
          }),
        ],
        url: tile_url,
      }),
      zIndex: 5,
    });

    mapbox_layer.setProperties({
      name: 'Terrain',
      id: 'Terrain',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    this.map.addLayer(mapbox_layer);
  },

  addBingLayers() {
    let api_key = config.BING_API_KEY;
    if (!api_key) {
      return;
    }

    // Bing's Road imagerySet
    let road = new ol.layer.Tile({
      source: new ol.source.BingMaps({
        key: api_key,
        imagerySet: 'Road',
      }),
      zIndex: 3,
    });

    road.setProperties({
      name: 'Bing Road',
      id: 'BingRoad',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    // Bing's AerialWithLabels imagerySet
    let hybrid = new ol.layer.Tile({
      source: new ol.source.BingMaps({
        key: api_key,
        imagerySet: 'AerialWithLabels',
      }),
      zIndex: 4,
    });

    hybrid.setProperties({
      name: 'Bing Satellite',
      id: 'BingSatellite',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    let map = this.map;
    map.addLayer(road);
    map.addLayer(hybrid);
  },

  addEmptyLayer() {
    let empty_layer = new ol.layer.Tile({});
    empty_layer.setProperties({
      name: 'Empty',
      id: 'Empty',
      base_layer: true,
      display_in_layer_switcher: true,
    });

    this.map.addLayer(empty_layer);
  },
});
