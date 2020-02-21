import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),

  model() {
    let ajax = this.ajax;
    let id = this.modelFor('groupflight').ids[0];

    return RSVP.hash({
      firstData: ajax.request(`/api/flights/${id}/?extended`),
      firstPath: ajax.request(`/api/flights/${id}/json`),
    });
  },


  setupController(controller) {
    this._super(...arguments);
    controller.set('groupflight', this.modelFor('groupflight').groupflight);
    controller.set('ids', this.modelFor('groupflight').ids);
    controller.set('club', this.modelFor('groupflight').club);
  },

});
