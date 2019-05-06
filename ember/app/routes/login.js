import Route from '@ember/routing/route';

import UnauthenticatedRouteMixin from 'ember-simple-auth/mixins/unauthenticated-route-mixin';

export default Route.extend(UnauthenticatedRouteMixin, {
  setupController() {
    this._super(...arguments);
    this.controllerFor('application').set('inLoginRoute', true);
  },

  resetController() {
    this._super(...arguments);
    this.controllerFor('application').set('inLoginRoute', false);
  },
});
