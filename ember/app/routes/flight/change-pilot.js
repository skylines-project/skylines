import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),
  account: service(),

  model() {
    let id = this.modelFor('flight').ids[0];

    let flight = this.ajax.request(`/api/flights/${id}/`).then(it => it.flight);

    let accountId = this.get('account.user.id');
    let clubId = this.get('account.club.id');
    let clubMembers = clubId
      ? this.ajax.request(`/api/users?club=${clubId}`).then(it => it.users.filter(user => user.id !== accountId))
      : [];

    return RSVP.hash({ id, flight, clubMembers });
  },
});
