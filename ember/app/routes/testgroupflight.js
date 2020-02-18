import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
    ajax: service(),
  //model includes groupflight, flights, and paths
  model({ groupflight_id }) {
    return this.ajax.request(`/api/testgroupflight/${groupflight_id}`);
  },
});

