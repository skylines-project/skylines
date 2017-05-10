import Ember from 'ember';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {
  ajax: Ember.inject.service(),
  account: Ember.inject.service(),

  async model() {
    let ajax = this.get('ajax');

    let accountId = this.get('account.user.id');
    let clubId = this.get('account.club.id');
    let clubMembers = [];
    if (clubId) {
      let { users } = await ajax.request(`/api/users?club=${clubId}`);
      clubMembers = users.filter(user => user.id !== accountId);
    }

    return { clubMembers };
  },
});
