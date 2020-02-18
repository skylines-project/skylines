import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
    ajax: service(),
  //model includes groupflight and ids
  model({ groupflight_id }) {
    return RSVP.hash({
    path: this.ajax.request(`/api/flights/${id}/json`),
    gfdata: this.ajax.request(`/api/testgroupflight/${groupflight_id}`),
    });
  },
});

