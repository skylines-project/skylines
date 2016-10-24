import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model({ user_ids }) {
    return this.get('ajax').request(`/api/live/${user_ids}`);
  },
});
