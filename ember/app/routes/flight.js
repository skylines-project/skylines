//import Route from '@ember/routing/route';
//
//export default Route.extend({
//  model(params) {
//    let ids = params.flight_ids.split(',').map(it => parseInt(it, 10));
//    return { ids };
//  },
//});


import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),

  async model(params) {
    var idsStr = params.flight_ids
    var ids = idsStr.split(',').map(it => parseInt(it, 10)); //This parses even with : in it
    if (idsStr.includes(':')) {  //groupflight
      var groupflight_id = idsStr.split(':')[0];
      var gfData = await this.ajax.request(`/api/groupflights/${groupflight_id}/`);
      var path = await this.ajax.request(`/api/groupflights/${ids[0]}/json`); //excludes contest traces
    } else {
      var path = await this.ajax.request(`/api/flights/${ids[0]}/json`);
    }
    var data = await this.ajax.request(`/api/flights/${ids[0]}/?extended`);
    return RSVP.hash({
        ids: ids,
        data: data,
        path: path,
        club: await this.ajax.request(`/api/clubs/${data.flight.club.id}`),
        gfData: gfData
      });
  },
});



