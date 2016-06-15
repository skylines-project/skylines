/* globals ol */

import Ember from 'ember';

export default Ember.Component.extend({
  tagName: '',

  source: null,
  contest: null,

  feature: Ember.computed(function() {
    let contest = this.get('contest');
    return new ol.Feature({
      geometry: contest.get('geometry'),
      sfid: contest.get('flightId'),
      color: contest.get('color'),
      type: 'contest',
    });
  }),

  didInsertElement() {
    this.get('source').addFeature(this.get('feature'));
  },

  willDestroyElement() {
    this.get('source').removeFeature(this.get('feature'));
  },
});
