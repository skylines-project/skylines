import { computed } from '@ember/object';
import Component from '@ember/component';
import ol from 'openlayers';

export default Component.extend({
  tagName: '',

  source: null,
  flight: null,

  feature: computed(function() {
    let flight = this.get('flight');
    return new ol.Feature({
      geometry: flight.get('geometry'),
      sfid: flight.get('id'),
      color: flight.get('color'),
      type: 'flight',
    });
  }),

  didInsertElement() {
    this._super(...arguments);
    this.get('source').addFeature(this.get('feature'));
  },

  willDestroyElement() {
    this._super(...arguments);
    this.get('source').removeFeature(this.get('feature'));
  },
});
