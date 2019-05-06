/* globals Cesium */

import Component from '@ember/component';
import { observer } from '@ember/object';
import { once } from '@ember/runloop';

import olcs from 'ol-cesium';

import config from 'skylines/config/environment';

export default Component.extend({
  tagName: '',

  enabled: false,
  map: null,

  enabledObserver: observer('enabled', function() {
    once(this, 'update');
  }),

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

    this.update();
  },

  update() {
    let enabled = this.enabled;

    this.ol3d.setEnabled(enabled);

    if (!enabled) {
      this.map.getView().setRotation(0);
    }
  },
});
