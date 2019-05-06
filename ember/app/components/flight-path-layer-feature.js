import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

export default Component.extend({
  tagName: '',

  source: null,
  flight: null,

  feature: computed(function() {
    let flight = this.flight;
    return new ol.Feature({
      geometry: flight.get('geometry'),
      sfid: flight.get('id'),
      color: flight.get('color'),
      type: 'flight',
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
