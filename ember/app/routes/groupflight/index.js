import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';

export default Route.extend({
  ajax: service(),

  model() {
    let { club_id } = this.paramsFor('club');
    return this.ajax.request(`/api/flights/${this.modelFor('groupflight').ids[0]}/json`);
  },


  setupController(controller) {
    this._super(...arguments);
    controller.set('groupflight', this.modelFor('groupflight').groupflight);
    controller.set('ids', this.modelFor('groupflight').ids);
    controller.set('club', this.modelFor('groupflight').club);
//    controller.set('firstPath', this.ajax.request(`/api/flights/${this.modelFor('groupflight').ids[0]}/json`));
  },

});
