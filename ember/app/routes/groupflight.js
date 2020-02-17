import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  model({ groupflight_id }) {
    return this.ajax.request(`/api/testgroupflight/${tgf_id}`);
  },
});
