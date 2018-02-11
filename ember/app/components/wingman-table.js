import { computed } from '@ember/object';
import Component from '@ember/component';

export default Component.extend({
  nearFlights: null,
  visibleFlights: null,

  nearFlightsWithColors: computed('nearFlights.[]', 'visibleFlights.[]', function() {
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
