import Route from '@ember/routing/route';

export default Route.extend({
  activate() {
    this._super(...arguments);
    this.controllerFor('application').set('onFreestyleRoute', true);
  },

  deactivate() {
    this._super(...arguments);
    this.controllerFor('application').set('onFreestyleRoute', false);
  },
});
