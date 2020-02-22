//import Route from '@ember/routing/route';
//import { inject as service } from '@ember/service';
//
//export default Route.extend({
//  ajax: service(),
//  ids: modelFor('groupflight').ids.split(',').map(it => parseInt(it, 10)),

//  model() {
////  console.log(ids);
//    let ids = this.modelFor('groupflight').ids.split(',').map(it => parseInt(it, 10));
//    return { ids };
//  },

import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
//import RSVP from 'rsvp';

export default Route.extend({
    ajax: service(),
  //model includes groupflight, ids, club
//    model({ groupflight_id }) {
//      return this.ajax.request(`/api/groupflights/${groupflight_id}`)
//    },

  afterModel() {
  console.log(this.modelFor('groupflight').ids[0]);
    this.transitionTo('flight', this.modelFor('groupflight').ids.join(','));
  },

});

//  model(params) {
//    let ids = params.flight_ids.split(',').map(it => parseInt(it, 10));
//    return { ids };
//  },

