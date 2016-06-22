import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model({airport_id}) {
    return this.get('ajax').request(`/flights/airport/${airport_id}`);
  },
});
