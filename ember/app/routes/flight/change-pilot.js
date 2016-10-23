import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),
  account: Ember.inject.service(),

  model() {
    let id = this.modelFor('flight').ids[0];

    let flight = this.get('ajax').request(`/api/flights/${id}/`).then(it => it.flight);

    let accountId = this.get('account.user.id');
    let clubId = this.get('account.club.id');
    let clubMembers = clubId ? this.get('ajax').request(`/users?club=${clubId}`)
      .then(it => it.users.filter(user => user.id !== accountId)) : [];

    return Ember.RSVP.hash({ id, flight, clubMembers });
  },
});
