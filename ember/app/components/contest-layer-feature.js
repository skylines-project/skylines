import Component from '@ember/component';
import { computed } from '@ember/object';

import ol from 'openlayers';

export default Component.extend({
  tagName: '',

  source: null,
  contest: null,

  feature: computed(function() {
    let contest = this.contest;
    return new ol.Feature({
      geometry: contest.get('geometry'),
      sfid: contest.get('flightId'),
      color: contest.get('color'),
      type: 'contest',
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
