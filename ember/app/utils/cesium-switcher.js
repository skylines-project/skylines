/* globals $, Cesium */

import Ember from 'ember';
import ol from 'openlayers';
import olcs from 'ol3-cesium';

const CesiumSwitcher = Ember.Object.extend({
  enabled: false,
  ol3d: null,

  init() {
    this._super(...arguments);

    let element = document.createElement('div');
    element.className = 'CesiumSwitcher ol-unselectable';

    ol.control.Control.call(this, {
      element: element,
    });

    $(element).on('click touchend', evt => {
      this.setMode(!this.enabled);
      evt.preventDefault();
    });

    this.setMode(this.enabled);

    this.set('element', element);
  },

  /**
   * Sets the 3d mode.
   * @param {bool} mode - Enabled or not
   */
  setMode(mode) {
    let element = this.get('element');

    if (mode) {
      element.innerHTML = '<img src="../../images/2d.png"/>';

      window.cesiumLoader.load()
        .then(() => this.enableCesium());

    } else {
      element.innerHTML = '<img src="../../images/3d.png"/>';

      let ol3d = this.get('ol3d');
      if (ol3d) {
        ol3d.setEnabled(false);
        this.getMap().getView().setRotation(0);
      }
    }

    this.set('enabled', mode);
  },


  /**
   * Enbables ol3-cesium.
   */
  enableCesium() {
    let ol3d = this.get('ol3d');
    if (!ol3d) {
      let map = this.getMap();

      ol3d = new olcs.OLCesium({map: map});

      let scene = ol3d.getCesiumScene();
      scene.terrainProvider = new Cesium.CesiumTerrainProvider({
        url: '//assets.agi.com/stk-terrain/world',
      });
      scene.globe.depthTestAgainstTerrain = true;

      this.set('ol3d', ol3d);
    }

    ol3d.setEnabled(true);
    ol3d.enableAutoRenderLoop();
  },


  /**
   * Returns the mode of cesium (3d or 2d).
   * @return {bool}
   */
  getMode() {
    return this.get('enabled');
  },

  /**
   * @param {slFlight} flight
   * @param {Array} fix_data
   */
  showPlane(flight, fix_data) {
    let lonlat = ol.proj.transform(fix_data.get('coordinate'), 'EPSG:3857', 'EPSG:4326');

    let position = Cesium.Cartesian3.fromDegrees(lonlat[0], lonlat[1],
        fix_data.get('alt-msl') + flight.get('geoid'));
    let modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(position,
        fix_data.get('heading') - Math.PI / 2, 0, 0);

    let entity = flight.get('entity');
    if (!entity) {
      let scene = this.get('ol3d').getCesiumScene();
      entity = Cesium.Model.fromGltf({
        modelMatrix: modelMatrix,
        url: '../../images/Cesium_Air.gltf',
        scale: 1,
        minimumPixelSize: 64,
        allowPicking: false,
      });
      scene.primitives.add(entity);
      flight.set('entity', entity);
    } else {
      entity.modelMatrix = modelMatrix;
      entity.show = true;
    }
  },


  /**
   * @param {slFlight} flight
   */
  hidePlane(flight) {
    let entity = flight.get('entity');
    if (entity) {
      entity.show = false;
    }
  },
});

ol.inherits(CesiumSwitcher, ol.control.Control);

export default CesiumSwitcher;
