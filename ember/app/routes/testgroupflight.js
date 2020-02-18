import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
//import RSVP from 'rsvp';

export default Route.extend({
    ajax: service(),
  //model includes groupflight and ids
  model({ groupflight_id }) {
    return this.ajax.request(`/api/testgroupflight/${groupflight_id}`)
//    return RSVP.hash({
//    firstpath: this.ajax.request(`/api/flight/${groupflight_id}/json`),
//    gfdata: this.ajax.request(`/api/testgroupflight/${groupflight_id}`),
//    });
  },
});

