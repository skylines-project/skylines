import Route from '@ember/routing/route';

export default class FlightRoute extends Route {
  model(params) {
    let ids = params.flight_ids.split(',').map(it => parseInt(it, 10));
    return { ids };
  }
}
