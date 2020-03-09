import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
//import RSVP from 'rsvp';

export default Route.extend({
    ajax: service(),
  //model includes groupflight, ids, club
    async model({ groupflight_id }) {
      return await this.ajax.request(`/api/groupflights/${groupflight_id}`)
  },
});
