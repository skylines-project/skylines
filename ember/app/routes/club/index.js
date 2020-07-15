import Route from '@ember/routing/route';

export default class IndexRoute extends Route {
  setupController(controller) {
    super.setupController(...arguments);
    controller.set('club', this.controllerFor('club').get('model'));
  }
}
