import Ember from 'ember';

export default Ember.Component.extend({
  fixCalc: Ember.inject.service(),
  pinnedFlights: Ember.inject.service(),

  selection: null,

  data: Ember.computed.map('fixCalc.fixes', function(fix, i) {
    let flight = fix.get('flight');
    let id = flight.get('id');
    let color = flight.get('color');
    let competitionId = flight.get('competition_id');
    let removable = (i !== 0);
    return { id, color, competitionId, removable, fix };
  }),

  selectable: Ember.computed.gt('data.length', 1),

  actions: {
    select(id) {
      let current = this.get('selection');
      this.getWithDefault('onSelectionChange', Ember.K)(current === id ? null : id);
    },

    // Remove a flight when the removal button has been pressed in the fix table.
    remove(id) {
      let flights = this.get('fixCalc.flights');
      let pinned = this.get('pinnedFlights');

      // never remove the first flight...
      if (flights.get('firstObject.id') != id) {
        flights.removeObjects(flights.filterBy('id', id));
        pinned.unpin(id);
      }
    },
  },
});
