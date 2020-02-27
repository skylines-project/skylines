import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  flights: null,
  fixes: null,
  selection: null,

  data: computed('fixes.@each.flight', function() {
    return this.fixes.map((fix, i) => {
      let flight = fix.get('flight');
      let id = flight.get('id');
      let color = flight.get('color');
      let competitionId = flight.get('competition_id') || flight.get('registration');
      let score = flight.get('score')*1000
      let distance = flight.get('distance')
      let triangleDistance = flight.get('triangleDistance')
      let removable = i !== 0;
      return { id, color, competitionId, score, distance, triangleDistance, removable, fix };
    });
  }),

  selectable: computed('data.[]', function() {
    return this.data.length > 1;
  }),

  actions: {
    select(id) {
      this.set('selection', this.selection === id ? null : id);
    },
  },
});
