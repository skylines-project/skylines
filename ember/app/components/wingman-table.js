import Ember from 'ember';

export default Ember.Component.extend(Ember.Evented, {
  nearFlights: [],
  visibleFlights: [],

  nearFlightsWithColors: Ember.computed('nearFlights.[]', 'visibleFlights.[]', function() {
    let { nearFlights, visibleFlights } = this.getProperties('nearFlights', 'visibleFlights');
    return nearFlights.map(it => {
      let id = it.flight.id;
      let visibleFlight = visibleFlights.find(flight => (flight.getID() === id));

      return {
        color: visibleFlight ? visibleFlight.get('color') : undefined,
        flight: it.flight,
        times: it.times,
      }
    });
  }),

  init() {
    this._super(...arguments);

    window.wingmanTable = this;
  },

  actions: {
    select(id) {
      this.trigger('select', id);
    }
  }
});
