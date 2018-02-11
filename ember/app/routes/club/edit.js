import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';

export default Route.extend({
  ajax: service(),

  setupController(controller) {
    this._super(...arguments);
    controller.set('club', this.controllerFor('club').get('model'));
  },
});
