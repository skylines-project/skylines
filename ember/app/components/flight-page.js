import Ember from 'ember';

export default Ember.Component.extend({
  fixCalc: Ember.inject.service(),
  pinnedFlights: Ember.inject.service(),

  tagName: '',

  actions: {
    selectWingman(id) {
      let fixCalc = this.get('fixCalc');
      let pinnedFlights = this.get('pinnedFlights');

      let flights = fixCalc.get('flights');
      let matches = flights.filterBy('id', id);
      if (matches.length !== 0) {
        flights.removeObjects(matches);
        pinnedFlights.unpin(id);
      } else {
        fixCalc.addFlightFromJSON(`/flights/${id}/json`);
        pinnedFlights.pin(id);
      }
    },
  },
});
