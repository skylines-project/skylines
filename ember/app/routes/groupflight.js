import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
//import RSVP from 'rsvp';

export default Route.extend({
    ajax: service(),
  //model includes groupflight and ids
  model({ groupflight_id }) {
    return this.ajax.request(`/api/groupflights/${groupflight_id}`)
  },
});

