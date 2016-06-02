/* global getPinnedFlights, pinFlight, unpinFlight */

import Ember from 'ember';

export default Ember.Service.extend({
  pinned: Ember.computed(function() {
    return getPinnedFlights();
  }),

  toggle(id) {
    let pinned = this.get('pinned');
    if (pinned.contains(id)) {
      unpinFlight(id);
      this.set('pinned', pinned.without(id));
    } else {
      pinFlight(id);
      this.set('pinned', pinned.concat([id]));
    }
  }
});
