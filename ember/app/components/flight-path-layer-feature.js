/* globals ol */

import Ember from 'ember';

export default Ember.Component.extend({
  tagName: '',

  source: null,
  flight: null,

  feature: Ember.computed(function() {
    let flight = this.get('flight');
    return new ol.Feature({
      geometry: flight.get('geometry'),
      sfid: flight.get('id'),
      color: flight.get('color'),
      type: 'flight'
    });
  }),

  didInsertElement() {
    this.get('source').addFeature(this.get('feature'));
  },

  willDestroyElement() {
    this.get('source').removeFeature(this.get('feature'));
  },
});
