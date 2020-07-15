import Route from '@ember/routing/route';

import UnauthenticatedRouteMixin from 'ember-simple-auth/mixins/unauthenticated-route-mixin';

export default class LoginRoute extends Route.extend(UnauthenticatedRouteMixin) {
  setupController() {
    super.setupController(...arguments);
    this.controllerFor('application').set('inLoginRoute', true);
  }

  resetController() {
    super.resetController(...arguments);
    this.controllerFor('application').set('inLoginRoute', false);
  }
}
