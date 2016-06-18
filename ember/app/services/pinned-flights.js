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
    this.set('pinned', this.get('pinned').concat([id]));
    pinFlight(id);
  },

  unpin(id) {
    this.set('pinned', this.get('pinned').without(id));
    unpinFlight(id);
  },

  toggle(id) {
    if (this.get('pinned').contains(id)) {
      this.unpin(id);
    } else {
      this.pin(id);
    }
  },
});
