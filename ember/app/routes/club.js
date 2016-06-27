import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model({ club_id }) {
    return this.get('ajax').request(`/clubs/${club_id}/`);
  },
});
