/* globals Cesium */

import Component from '@ember/component';
import { action } from '@ember/object';

import { transform } from 'ol/proj';

export default class CesiumPlaneModel extends Component {
  tagName = '';

  scene = null;
  fix = null;

  entity = Cesium.Model.fromGltf({
    url: '../../3d/AS21.glb',
    scale: 1,
    minimumPixelSize: 64,
    allowPicking: false,
  });

  @action
  update([coordinate, heading]) {
    let lonlat = transform(coordinate, 'EPSG:3857', 'EPSG:4326');

    let position = Cesium.Cartesian3.fromDegrees(lonlat[0], lonlat[1], lonlat[2]);
    let rotation = new Cesium.HeadingPitchRoll(heading, 0, 0);

    this.entity.modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(position, rotation);
  }

  didInsertElement() {
    super.didInsertElement(...arguments);
    this.scene.primitives.add(this.entity);
  }

  willDestroyElement() {
    super.willDestroyElement(...arguments);
    this.scene.primitives.remove(this.entity);
  }
}
