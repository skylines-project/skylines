/* globals Cesium */

import Component from '@ember/component';

import { transform } from 'ol/proj';

import safeComputed from '../computed/safe-computed';

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

  @safeComputed('coordinate', coordinate => {
    let lonlat = transform(coordinate, 'EPSG:3857', 'EPSG:4326');
    return Cesium.Cartesian3.fromDegrees(lonlat[0], lonlat[1], lonlat[2]);
  })
  position;

  didReceiveAttrs() {
    super.didReceiveAttrs(...arguments);
    this.entity.modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(
      this.position,
      new Cesium.HeadingPitchRoll(this.heading, 0, 0),
    );
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
