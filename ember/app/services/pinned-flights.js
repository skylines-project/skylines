/* global showPinnedFlightsLink */

import Ember from 'ember';

export default Ember.Service.extend({
  init() {
    this._super(...arguments);
    this.load();

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

  load() {
    let pinned = [];

    var cookie = Ember.$.cookie('SkyLines_pinnedFlights');
    if (cookie) {
      pinned = cookie.split(',').map(it => parseInt(it, 10));
    }

    this.set('pinned', pinned);
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

