import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model({ user_id }) {
    return this.get('ajax').request(`/users/${user_id}/?extended`);
  },
});
