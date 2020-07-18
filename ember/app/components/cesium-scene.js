/* globals Cesium */

import Component from '@glimmer/component';
import { tracked } from '@glimmer/tracking';

import olcs from 'ol-cesium';

import config from 'skylines/config/environment';

export default class CesiumScene extends Component {
  @tracked ol3d;
  @tracked scene;

  constructor() {
    super(...arguments);

    let ol3d = new olcs.OLCesium({ map: this.args.map });

    Cesium.Ion.defaultAccessToken = config.CESIUM_TOKEN;

    let scene = ol3d.getCesiumScene();
    scene.terrainProvider = new Cesium.CesiumTerrainProvider({
      url: Cesium.IonResource.fromAssetId(1),
    });
    scene.globe.depthTestAgainstTerrain = true;

    this.ol3d = ol3d;
    this.scene = scene;

    this.ol3d.setEnabled(true);
  }

  willDestroy() {
    this.args.map.getView().setRotation(0);
    this.ol3d.setEnabled(false);
  }
}
