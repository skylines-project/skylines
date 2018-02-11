import { inject as service } from '@ember/service';
import Route from '@ember/routing/route';

export default Route.extend({
  ajax: service(),

  model({ club_id }) {
    return this.get('ajax').request(`/api/clubs/${club_id}`);
  },
});
