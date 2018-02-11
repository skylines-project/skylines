import Component from '@ember/component';
import { gt } from 'ember-awesome-macros';
import { map } from 'ember-awesome-macros/array';

export default Component.extend({
  flights: null,
  fixes: null,
  selection: null,

  data: map('fixes', function(fix, i) {
    let flight = fix.get('flight');
    let id = flight.get('id');
    let color = flight.get('color');
    let competitionId = flight.get('competition_id') || flight.get('registration');
    let removable = (i !== 0);
    return { id, color, competitionId, removable, fix };
  }),

  selectable: gt('data.length', 1),

  actions: {
    select(id) {
      this.set('selection', this.get('selection') === id ? null : id);
    },
  },
});
