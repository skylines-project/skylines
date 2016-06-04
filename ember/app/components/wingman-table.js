import Ember from 'ember';

export default Ember.Component.extend(Ember.Evented, {
  init() {
    this._super(...arguments);

    window.wingmanTable = this;
  },

  setFlightColor(id, color) {
    let nearFlight = this.get('nearFlights').findBy('flight.id', id);
    if (nearFlight) {
      Ember.set(nearFlight, 'color', color);
    }
  },

  actions: {
    select(id) {
      this.trigger('select', id);
    }
  }
});
