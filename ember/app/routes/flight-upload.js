import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),
  account: Ember.inject.service(),

  model() {
    let ajax = this.get('ajax');

    let csrfToken = ajax.request('/flights/upload/csrf').then(it => it.token);

    let accountId = this.get('account.user.id');
    let clubId = this.get('account.club.id');
    let clubMembers = [];
    if (clubId) {
      clubMembers = ajax.request(`/users?club=${clubId}`).then(it => it.users.filter(user => user.id !== accountId));
    }

    return Ember.RSVP.hash({ clubMembers, csrfToken });
  },
});
