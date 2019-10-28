import Component from '@ember/component';
import { computed } from '@ember/object';

export default Component.extend({
  tagName: '',
  flights: null,
  fixes: null,
  selection: null,

  data: computed('fixes.@each.flight', function() {
    return this.fixes.map((fix, i) => {
      let flight = fix.get('flight');
      let id = flight.get('id');
      let color = flight.get('color');
      let competitionId = flight.get('competition_id') || flight.get('registration');
      let removable = i !== 0;
      return { id, color, competitionId, removable, fix };
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
