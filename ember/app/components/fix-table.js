/* global unpinFlight */

import Ember from 'ember';

export default Ember.Component.extend(Ember.Evented, {
  flights: [],
  time: null,
  selection: null,

  data: Ember.computed('flights.[]', 'time', function() {
    let time = this.get('time');
    return this.get('flights').map((flight, i) => {
      let id = flight.getID();
      let color = flight.getColor();
      let competitionId = flight.getCompetitionID();
      let removable = (i !== 0);
      let fix = flight.getFixData(time);
      return {id, color, competitionId, removable, fix};
    });
  }),

  selectable: Ember.computed.gt('data.length', 1),

  init() {
    this._super(...arguments);

    window.fixTable = this;
  },

  actions: {
    select(id) {
      if (this.get('selectable')) {
        var current = this.get('selection');
        this.set('selection', current === id ? null : id);
      }
    },

    remove(id) {
      this.trigger('remove_flight', id);
      unpinFlight(id);
    },
  },
});
