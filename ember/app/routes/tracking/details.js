import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  model({ user_ids }) {
    return this.ajax.request(`/api/live/${user_ids}`);
  },
});
