import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model() {
    let id = this.modelFor('flight').ids[0];
    return this.get('ajax').request(`/flights/${id}/?extended`);
  },

  setupController(controller) {
    this._super(...arguments);
    controller.set('ids', this.modelFor('flight').ids);
  },
});
