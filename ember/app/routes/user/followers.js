import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';

export default Route.extend({
  ajax: service(),

  model() {
    let { user_id } = this.paramsFor('user');
    return this.get('ajax').request(`/api/users/${user_id}/followers`);
  },

  setupController(controller, model) {
    this._super(...arguments);
    controller.set('user', this.modelFor('user'));
    controller.set('followers', model.followers);
  },
});
