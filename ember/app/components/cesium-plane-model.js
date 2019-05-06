/* globals Cesium */

import Component from '@ember/component';

import ol from 'openlayers';

import safeComputed from '../computed/safe-computed';

export default Component.extend({
  tagName: '',

  scene: null,
  fix: null,

  entity: null,

  position: safeComputed('coordinate', coordinate => {
    let lonlat = ol.proj.transform(coordinate, 'EPSG:3857', 'EPSG:4326');
    return Cesium.Cartesian3.fromDegrees(lonlat[0], lonlat[1], lonlat[2]);
  }),

  init() {
    this._super(...arguments);

    this.set(
      'entity',
      Cesium.Model.fromGltf({
        url: '../../3d/AS21.glb',
        scale: 1,
        minimumPixelSize: 64,
        allowPicking: false,
      }),
    );
  },

  didReceiveAttrs() {
    this._super(...arguments);
    this.entity.modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(
      this.position,
      new Cesium.HeadingPitchRoll(this.heading - Math.PI / 2, 0, 0),
    );
  },

  didInsertElement() {
    this._super(...arguments);
    this.scene.primitives.add(this.entity);
  },

  willDestroyElement() {
    this._super(...arguments);
    this.scene.primitives.remove(this.entity);
  },
});
