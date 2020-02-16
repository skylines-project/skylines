import Route from '@ember/routing/route';

export default Route.extend({
  setupController(controller) {
    this._super(...arguments);
    controller.set('groupflight', this.controllerFor('groupflight').get('model'));
  },
});
