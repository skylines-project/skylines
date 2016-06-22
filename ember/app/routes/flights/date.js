import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model({date}) {
    return this.get('ajax').request(`/flights/date/${date}`);
  },
});
