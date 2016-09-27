import Ember from 'ember';

export default Ember.Component.extend({
  nearFlights: [],
  visibleFlights: [],

  nearFlightsWithColors: Ember.computed('nearFlights.[]', 'visibleFlights.[]', function() {
    let { nearFlights, visibleFlights } = this.getProperties('nearFlights', 'visibleFlights');
    return nearFlights.map(it => {
      let id = it.flight.id;
      let visibleFlight = visibleFlights.findBy('id', id);

      return {
        color: visibleFlight ? visibleFlight.get('color') : undefined,
        flight: it.flight,
        times: it.times,
      };
    });
  }),

  actions: {
    select(id) {
      this.get('onSelect')(id);
    },
  },
});
