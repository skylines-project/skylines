import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  model({ user_id }) {
    return this.ajax.request(`/api/users/${user_id}?extended`);
  },
});
