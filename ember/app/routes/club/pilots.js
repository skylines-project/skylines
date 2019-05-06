import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  model() {
    let { club_id } = this.paramsFor('club');
    return this.ajax.request(`/api/users?club=${club_id}`);
  },

  setupController(controller) {
    this._super(...arguments);
    controller.set('club', this.controllerFor('club').get('model'));
  },
});
