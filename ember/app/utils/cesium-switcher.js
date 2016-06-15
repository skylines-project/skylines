/* globals Cesium */

import Ember from 'ember';
import ol from 'openlayers';
import olcs from 'ol3-cesium';

export default Ember.Object.extend({
  ol3d: null,

  /**
   * Sets the 3d mode.
   * @param {bool} mode - Enabled or not
   */
  setMode(mode) {
    if (mode) {
      window.cesiumLoader.load()
        .then(() => this.enableCesium());

    } else {
      let ol3d = this.get('ol3d');
      if (ol3d) {
        ol3d.setEnabled(false);
        this.get('map').getView().setRotation(0);
      }
    }
  },


  /**
   * Enbables ol3-cesium.
   */
  enableCesium() {
    let ol3d = this.get('ol3d');
    if (!ol3d) {
      let map = this.get('map');

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
