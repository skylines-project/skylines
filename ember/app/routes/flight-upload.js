import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Route.extend(AuthenticatedRouteMixin, {
  ajax: service(),
  account: service(),

  async model() {
    let ajax = this.ajax;

    let accountId = this.get('account.user.id');
    let clubId = this.get('account.club.id');
    let clubMembers = [];
    if (clubId) {
      let { users } = await ajax.request(`/api/users?club=${clubId}`);
      clubMembers = users.filter(user => user.id !== accountId);
    }

    return { clubMembers };
  },

  setupController(controller) {
    this._super(...arguments);

    controller.set('result', null);
  },
});
