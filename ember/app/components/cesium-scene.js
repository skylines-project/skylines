/* globals Cesium */

import Component from '@ember/component';

import olcs from 'ol-cesium';

import config from 'skylines/config/environment';

export default Component.extend({
  tagName: '',

  map: null,

  init() {
    this._super(...arguments);

    let ol3d = new olcs.OLCesium({ map: this.map });

    Cesium.Ion.defaultAccessToken = config.CESIUM_TOKEN;

    let scene = ol3d.getCesiumScene();
    scene.terrainProvider = new Cesium.CesiumTerrainProvider({
      url: Cesium.IonResource.fromAssetId(1),
    });
    scene.globe.depthTestAgainstTerrain = true;

    this.set('ol3d', ol3d);
    this.set('scene', scene);

    this.ol3d.setEnabled(true);
  },

  willDestroy() {
    this.map.getView().setRotation(0);
    this.ol3d.setEnabled(false);
  },
});
