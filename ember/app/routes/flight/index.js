import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),

  model() {
    let ajax = this.ajax;


//    let id = this.modelFor('flight').ids[0];
//    return RSVP.hash({
//      data: ajax.request(`/api/flights/${id}/?extended`),
//      path: ajax.request(`/api/flights/${id}/json`),
//    });
//  },

    let ids = this.modelFor('flight').ids
    console.log(ids.length)
    if (ids.length > 1) {
      return RSVP.hash({
        data: ajax.request(`/api/flights/${ids[0]}/?extended`),
        path: ajax.request(`/api/groupflights/${ids[0]}/json`),
      });
    }
    else {
      return RSVP.hash({
        data: ajax.request(`/api/flights/${ids[0]}/?extended`),
        path: ajax.request(`/api/flights/${ids[0]}/json`),
      });
    }
  },



  setupController(controller, model) {
    this._super(...arguments);
    controller.set('ids', this.modelFor('flight').ids);
    controller.set('model', model.data);
    controller.set('_primaryFlightPath', model.path);
  },
});
