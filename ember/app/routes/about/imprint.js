import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  model() {
    return this.ajax.request('/api/imprint');
  },
});
