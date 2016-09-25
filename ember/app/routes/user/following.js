import Ember from 'ember';

export default Ember.Route.extend({
  ajax: Ember.inject.service(),

  model() {
    let { user_id } = this.paramsFor('user');
    return this.get('ajax').request(`/users/${user_id}/following`);
  },

  setupController(controller, model) {
    this._super(...arguments);
    controller.set('user', this.modelFor('user'));
    controller.set('following', model.following);
  },
});
