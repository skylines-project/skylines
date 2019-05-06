import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

export default Component.extend({
  tagName: '',

  source: null,
  location: null,

  feature: computed(function() {
    let location = this.location;
    let transformed = ol.proj.transform(location, 'EPSG:4326', 'EPSG:3857');

    return new ol.Feature({
      geometry: new ol.geom.Point(transformed),
    });
  }),

  didInsertElement() {
    this._super(...arguments);
    this.source.addFeature(this.feature);
  },

  willDestroyElement() {
    this._super(...arguments);
    this.source.removeFeature(this.feature);
  },
});
