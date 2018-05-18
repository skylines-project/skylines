import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';

export default Route.extend({
  ajax: service(),

  model() {
    return this.ajax.request('/api/clubs');
  },
});
