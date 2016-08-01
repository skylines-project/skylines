import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model() {
    let { club_id } = this.paramsFor('club');
    return this.get('ajax').request(`/users?club=${club_id}`);
  },

  setupController(controller) {
    this._super(...arguments);
    controller.set('club', this.controllerFor('club').get('model'));
  },
});
