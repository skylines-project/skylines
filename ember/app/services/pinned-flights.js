import Ember from 'ember';

export default Ember.Service.extend({
  cookies: Ember.inject.service(),

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

    let cookie = this.get('cookies').read('SkyLines_pinnedFlights');
    if (cookie) {
      pinned = cookie.split(',').map(it => parseInt(it, 10));
    }

    this.set('pinned', pinned);
  },

  save() {
    this.get('cookies').write('SkyLines_pinnedFlights', this.get('pinned').join(','), { path: '/' });
  },

  toggle(id) {
    if (this.get('pinned').contains(id)) {
      this.unpin(id);
    } else {
      this.pin(id);
    }
  },
});

