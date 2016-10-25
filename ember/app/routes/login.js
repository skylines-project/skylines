import Ember from 'ember';
import UnauthenticatedRouteMixin from 'ember-simple-auth/mixins/unauthenticated-route-mixin';

export default Ember.Route.extend(UnauthenticatedRouteMixin, {
  setupController() {
    this._super(...arguments);
    this.controllerFor('application').set('inLoginRoute', true);
  },

  resetController() {
    this._super(...arguments);
    this.controllerFor('application').set('inLoginRoute', false);
  },
});
