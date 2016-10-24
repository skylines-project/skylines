import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model({ club_id }) {
    return this.get('ajax').request(`/api/clubs/${club_id}`);
  },
});
