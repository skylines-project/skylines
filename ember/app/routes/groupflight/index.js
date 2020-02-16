import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  model({ groupflight_id }) {
    return this.ajax.request(`/api/groupflight/${groupflight_id}`);
  },

  setupController(controller, model) {
    this._super(...arguments);
    controller.set('ids', this.modelFor('groupflight').ids);
    controller.set('model', model.data);
    controller.set('_primaryFlightPath', model.path);
  },
});
