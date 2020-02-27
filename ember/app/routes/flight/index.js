import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),

  model() {
    return this.modelFor('flight')
  },

  setupController(controller, model) {
    this._super(...arguments);
    controller.set('_primaryFlightPath', model.path);
  },
});
