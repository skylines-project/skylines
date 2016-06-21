import Ember from 'ember';

export default Ember.Route.extend({
  beforeModel(transition) {
    let id = transition.params && transition.params.flight && transition.params.flight.flight_id;
    if (!id.match(/\d+/)) {
      return this.transitionTo('flights.list', id);
    }
  },

  model() {},
});
