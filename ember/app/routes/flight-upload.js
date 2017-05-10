import Ember from 'ember';
import RSVP from 'rsvp';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {
  ajax: Ember.inject.service(),
  account: Ember.inject.service(),

  model() {
    let ajax = this.get('ajax');

    let accountId = this.get('account.user.id');
    let clubId = this.get('account.club.id');
    let clubMembers = [];
    if (clubId) {
      clubMembers = ajax.request(`/api/users?club=${clubId}`).then(it => it.users.filter(user => user.id !== accountId));
    }

    return RSVP.hash({ clubMembers });
  },
});
