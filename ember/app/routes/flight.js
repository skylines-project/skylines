import Route from '@ember/routing/route';
import { inject as service } from '@ember/service';
import RSVP from 'rsvp';

export default Route.extend({
  ajax: service(),

  model(params) {
    let paramsStr = params.flight_ids
    console.log(params);
    console.log(paramsStr);

    console.log(typeof paramsStr);
    if (paramsStr.includes(':')) {  //groupflight
      let groupflight_id = paramsStr.split(':')[0];
      let groupflightFetch = this.ajax.request(`/api/groupflights/${groupflight_id}/`);
      console.log(paramsStr.split(':')[1].split(',').map(it => parseInt(it, 10)))
      let idsList = paramsStr.split(':')[1].split(',').map(it => parseInt(it, 10));
    }
    else {
//        let groupflightFetch = Null;
        let idsList = paramsStr.split(',').map(it => parseInt(it, 10));
    }
    let dataFetch = this.ajax.request(`/api/flights/${ids[0]}/?extended`);
    return RSVP.hash({
        ids: idsList,
        data: dataFetch,
        path: this.ajax.request(`/api/groupflights/${ids[0]}/json`), //excludes contest traces
        club: this.ajax.request(`/api/clubs/${dataFetch.flight.club_id}`),
        groupflight: groupflightFetch
      });
  },
});



