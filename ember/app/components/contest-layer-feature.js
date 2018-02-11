import { computed } from '@ember/object';
import Component from '@ember/component';
import ol from 'openlayers';

export default Component.extend({
  tagName: '',

  source: null,
  contest: null,

  feature: computed(function() {
    let contest = this.get('contest');
    return new ol.Feature({
      geometry: contest.get('geometry'),
      sfid: contest.get('flightId'),
      color: contest.get('color'),
      type: 'contest',
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
