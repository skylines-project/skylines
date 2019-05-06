import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),

  model() {
    let id = this.modelFor('flight').ids[0];

    let flight = this.ajax.request(`/api/flights/${id}/`).then(it => it.flight);
    let aircraftModels = this.ajax.request('/api/aircraft-models').then(it => it.models);

    return RSVP.hash({ id, flight, aircraftModels });
  },
});
