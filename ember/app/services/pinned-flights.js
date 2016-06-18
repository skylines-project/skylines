/* global getPinnedFlights, pinFlight, unpinFlight */

import Ember from 'ember';

export default Ember.Service.extend({
  pinned: Ember.computed(function() {
    return getPinnedFlights();
  }),

  init() {
    this._super(...arguments);
    window.pinnedFlightsService = this;
  },

  pin(id) {
    pinFlight(id);
    this.set('pinned', this.get('pinned').concat([id]));
  },

  unpin(id) {
    unpinFlight(id);
    this.set('pinned', this.get('pinned').without(id));
  },

  toggle(id) {
    if (this.get('pinned').contains(id)) {
      this.unpin(id);
    } else {
      this.pin(id);
    }
  },
});
