import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default class EditRoute extends Route {
  @service ajax;

  setupController(controller) {
    super.setupController(...arguments);
    controller.set('club', this.controllerFor('club').get('model'));
  }
}
