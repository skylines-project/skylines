import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),

  model() {
    console.log(this.modelFor('flight').groupflight);
//    let ids = this.modelFor('flight').ids;
//    console.log(ids.length);
    if (this.modelFor('flight').groupflight) {
      return RSVP.hash({
        data: this.modelFor('flight').data,
        path: this.modelFor('flight').path,
        club: this.ajax.request(`/api/clubs/${this.modelFor('flight').groupflight.club_id}`),
        groupflight: this.modelFor('flight').groupflight,
//        ids: this.modelFor('flight').ids
      });
    }
    else {
      return RSVP.hash({
        data: this.modelFor('flight').data,
        path: this.modelFor('flight').path,
      });
    }
  },

  setupController(controller, model) {
    this._super(...arguments);
//    controller.set('ids', this.modelFor('flight').ids);
//    controller.set('model', model);
    controller.set('_primaryFlightPath', model.path);
  },
});
