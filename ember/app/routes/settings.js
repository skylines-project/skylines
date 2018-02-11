import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Route.extend(AuthenticatedRouteMixin, {
  ajax: service(),

  model() {
    return this.get('ajax').request('/api/settings/');
  },
});
