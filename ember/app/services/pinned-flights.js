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

/**
 * Saves the flight id into the pinnedFlights cookie
 *
 * @param {Number} sfid SkyLines flight ID.
 */
function pinFlight(sfid) {
  var pinnedFlights = getPinnedFlights();
  for (var i = 0; i < pinnedFlights.length; i++) {
    if (pinnedFlights[i] == sfid) return;
  }

  pinnedFlights.push(sfid);
  Ember.$.cookie('SkyLines_pinnedFlights', pinnedFlights.join(','), { path: '/' });

  // show pinned flights link in list view if found in DOM
  showPinnedFlightsLink();
}

/**
 * Removes a pinned flight from the pinnedFlights cookie
 *
 * @param {Number} sfid SkyLines flight ID.
 */
function unpinFlight(sfid) {
  var pinnedFlights = getPinnedFlights();
  var temp = [];

  for (var i = 0; i < pinnedFlights.length; i++) {
    if (pinnedFlights[i] != sfid) temp.push(pinnedFlights[i]);
  }

  Ember.$.cookie('SkyLines_pinnedFlights', temp.join(','), { path: '/' });

  // toggle the pinned flights link in list view if found in DOM
  showPinnedFlightsLink();
}

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
