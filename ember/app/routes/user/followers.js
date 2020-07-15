import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class FollowersRoute extends Route {
  @service ajax;

  model() {
    let { user_id } = this.paramsFor('user');
    return this.ajax.request(`/api/users/${user_id}/followers`);
  }

  setupController(controller, model) {
    super.setupController(...arguments);
    controller.set('user', this.modelFor('user'));
    controller.set('followers', model.followers);
  }
}
