import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default class SettingsRoute extends Route.extend(AuthenticatedRouteMixin) {
  @service ajax;

  model() {
    return this.ajax.request('/api/settings/');
  }
}
