import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class FlightUploadRoute extends Route {
  @service ajax;
  @service account;
  @service session;

  beforeModel(transition) {
    this.session.requireAuthentication(transition, 'login');
  }

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
  }

  setupController(controller) {
    super.setupController(...arguments);
    controller.set('result', null);
  }
}
