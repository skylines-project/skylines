import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  model({ tgf_id }) {
    return this.ajax.request(`/api/testgroupflight/${tgf_id}`);
  },

//    model() {
//    return this.ajax.request(`/api/testgroupflight`);
//  },

});
