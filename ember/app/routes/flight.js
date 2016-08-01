import Ember from 'ember';

export default Ember.Route.extend({
  model(params) {
    let ids = params.flight_ids.split(',').map(it => parseInt(it, 10));
    return { ids };
  },
});
