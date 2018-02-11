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

    this.set('entity', Cesium.Model.fromGltf({
      url: '../../images/Cesium_Air.glb',
      scale: 1,
      minimumPixelSize: 64,
      allowPicking: false,
    }));
  },

  didReceiveAttrs() {
    this._super(...arguments);
    this.get('entity').modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(
      this.get('position'), new Cesium.HeadingPitchRoll(this.get('heading') - Math.PI / 2, 0, 0));
  },

  didInsertElement() {
    this._super(...arguments);
    this.get('scene').primitives.add(this.get('entity'));
  },

  willDestroyElement() {
    this._super(...arguments);
    this.get('scene').primitives.remove(this.get('entity'));
  },
});
