/* global showPinnedFlightsLink */

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
    this.save();
  },

  unpin(id) {
    this.set('pinned', this.get('pinned').without(id));
    this.save();
  },

  save() {
    Ember.$.cookie('SkyLines_pinnedFlights', this.get('pinned').join(','), { path: '/' });

    // show pinned flights link in list view if found in DOM
    showPinnedFlightsLink();
  },

  toggle(id) {
    if (this.get('pinned').contains(id)) {
      this.unpin(id);
    } else {
      this.pin(id);
    }
  },
});

/**
 * Gets all pinned flights from the pinnedFlight cookie
 *
 * @return {Array<Number>} Array of SkyLines flight IDs.
 */
function getPinnedFlights() {
  var cookie = Ember.$.cookie('SkyLines_pinnedFlights');

  if (cookie) {
    var pinnedFlights = cookie.split(',');

    for (var i = 0; i < pinnedFlights.length; i++) {
      pinnedFlights[i] = parseInt(pinnedFlights[i]);
    }

    return pinnedFlights;
  }

  return [];
}
