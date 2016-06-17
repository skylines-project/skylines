/* globals Cesium */

import Ember from 'ember';
import ol from 'openlayers';

import safeComputed from '../utils/safe-computed';

export default Ember.Component.extend({
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
      url: '../../images/Cesium_Air.gltf',
      scale: 1,
      minimumPixelSize: 64,
      allowPicking: false,
    }));
  },

  didReceiveAttrs() {
    this.get('entity').modelMatrix = Cesium.Transforms.headingPitchRollToFixedFrame(
      this.get('position'), this.get('heading') - Math.PI / 2, 0, 0);
  },

  didInsertElement() {
    this.get('scene').primitives.add(this.get('entity'));
  },

  willDestroyElement() {
    this.get('scene').primitives.remove(this.get('entity'));
  },
});
