/* globals Cesium */

import { action } from '@ember/object';
import Component from '@glimmer/component';

import { toLonLat } from 'ol/proj';

export default class CesiumPlaneModel extends Component {
  entity = Cesium.Model.fromGltf({
    url: '../../3d/AS21.glb',
    scale: 1,
    minimumPixelSize: 64,
    allowPicking: false,
  });

  @action
  update([coordinate, heading]) {
    let lonlat = toLonLat(coordinate);

    let position = Cesium.Cartesian3.fromDegrees(lonlat[0], lonlat[1], lonlat[2]);
    let rotation = new Cesium.HeadingPitchRoll(heading, 0, 0);

    this.entity.modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(position, rotation);
  }

  constructor() {
    super(...arguments);
    this.args.scene.primitives.add(this.entity);
  }

  willDestroy() {
    super.willDestroy(...arguments);
    this.args.scene.primitives.remove(this.entity);
  }
}
