/* globals Cesium */

import { once } from '@ember/runloop';

import { observer } from '@ember/object';
import Component from '@ember/component';
import olcs from 'ol-cesium';

export default Component.extend({
  tagName: '',

  enabled: false,
  map: null,

  enabledObserver: observer('enabled', function() {
    once(this, 'update');
  }),

  init() {
    this._super(...arguments);

    let ol3d = new olcs.OLCesium({ map: this.get('map') });

    let scene = ol3d.getCesiumScene();
    scene.terrainProvider = new Cesium.CesiumTerrainProvider({
      url: '//assets.agi.com/stk-terrain/world',
    });
    scene.globe.depthTestAgainstTerrain = true;

    this.set('ol3d', ol3d);
    this.set('scene', scene);

    this.update();
  },

  update() {
    let enabled = this.get('enabled');

    this.get('ol3d').setEnabled(enabled);

    if (!enabled) {
      this.get('map').getView().setRotation(0);
    }
  },
});
